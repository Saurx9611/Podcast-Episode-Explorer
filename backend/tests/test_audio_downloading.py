import os
import io
import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
from fastapi.testclient import TestClient

from backend.main import app
from backend.core.database import SessionLocal, init_db
from backend.models.episode import Episode
from backend.models.podcast import Podcast
from backend.repositories.episode_repo import EpisodeRepository
from backend.repositories.podcast_repo import PodcastRepository
from backend.repositories.processing_repo import ProcessingRepository
from backend.storage.local_storage import LocalStorageService
from backend.services.audio_downloader_service import AudioDownloaderService, derive_clean_filename
from backend.core.exceptions import ValidationException, NotFoundException

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_derive_clean_filename():
    ep = Episode(title="Episode #42: Super AI & Distributed Systems!?")
    clean = derive_clean_filename(ep, "https://cdn.example.com/audio/my_recording.mp3")
    assert clean.endswith(".mp3")
    assert "Episode__42__Super_AI___Distributed_Systems" in clean

@pytest.mark.anyio
async def test_storage_save_stream(tmp_path):
    storage = LocalStorageService(storage_dir=str(tmp_path))

    async def fake_stream():
        for i in range(5):
            yield b"AUDIO_CHUNK_DATA_" + str(i).encode()

    url, filename, size, mime = await storage.save_stream(
        stream_iterator=fake_stream(),
        filename="test_stream.mp3",
        content_type="audio/mpeg",
    )

    assert url.startswith("/storage/")
    assert "test_stream.mp3" in filename
    assert size == len(b"AUDIO_CHUNK_DATA_0") * 5
    assert storage.file_exists(url) is True

    # Test cleanup on failure / empty stream
    async def empty_stream():
        if False:
            yield b""

    with pytest.raises(ValidationException, match="empty"):
        await storage.save_stream(
            stream_iterator=empty_stream(),
            filename="empty.mp3",
            content_type="audio/mpeg",
        )

@pytest.mark.anyio
async def test_audio_downloader_successful(db_session, tmp_path):
    storage = LocalStorageService(storage_dir=str(tmp_path))
    downloader = AudioDownloaderService(storage_service=storage)
    ep_repo = EpisodeRepository(db_session)

    # Create episode in DB
    ep = Episode(
        title="Test Ingestion Episode",
        audio_url="https://audio.example.com/podcast/ep1.mp3",
        status="uploaded"
    )
    created_ep = ep_repo.create(ep)

    try:
        # Mock httpx streaming response
        mock_chunks = [b"ID3\x03\x00\x00\x00", b"FAKE_AUDIO_SAMPLE_STREAM_DATA_CHUNK_1", b"_CHUNK_2"]
        
        async def mock_aiter(chunk_size=None):
            for c in mock_chunks:
                yield c

        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.headers = {"content-type": "audio/mpeg", "content-length": "1000"}
        mock_resp.aiter_bytes = mock_aiter

        mock_stream_ctx = AsyncMock()
        mock_stream_ctx.__aenter__.return_value = mock_resp
        mock_stream_ctx.__aexit__.return_value = None

        with patch("httpx.AsyncClient.stream", return_value=mock_stream_ctx):
            with patch("backend.services.audio_downloader_service.validate_feed_url", return_value="https://audio.example.com/podcast/ep1.mp3"):
                updated = await downloader.download_episode_audio(db=db_session, episode_id=created_ep.id)
                assert updated.status == "uploaded"
                assert updated.audio_url.startswith("/storage/")
                assert updated.file_size == sum(len(c) for c in mock_chunks)
                assert storage.file_exists(updated.audio_url) is True

        # Test duplicate download (idempotent - skips re-download)
        idempotent_ep = await downloader.download_episode_audio(db=db_session, episode_id=created_ep.id)
        assert idempotent_ep.audio_url == updated.audio_url

    finally:
        ep_repo.delete(created_ep.id)

@pytest.mark.anyio
async def test_audio_downloader_404_error(db_session, tmp_path):
    storage = LocalStorageService(storage_dir=str(tmp_path))
    downloader = AudioDownloaderService(storage_service=storage)
    ep_repo = EpisodeRepository(db_session)

    ep = Episode(
        title="404 Missing Audio Episode",
        audio_url="https://audio.example.com/missing.mp3",
        status="uploaded"
    )
    created_ep = ep_repo.create(ep)

    try:
        mock_resp = AsyncMock()
        mock_resp.status_code = 404
        mock_resp.headers = {}
        mock_stream_ctx = AsyncMock()
        mock_stream_ctx.__aenter__.return_value = mock_resp
        mock_stream_ctx.__aexit__.return_value = None

        with patch("httpx.AsyncClient.stream", return_value=mock_stream_ctx):
            with patch("backend.services.audio_downloader_service.validate_feed_url", return_value="https://audio.example.com/missing.mp3"):
                with pytest.raises(ValidationException, match="404"):
                    await downloader.download_episode_audio(db=db_session, episode_id=created_ep.id)

                failed_ep = ep_repo.get_by_id(created_ep.id)
                assert failed_ep.status == "failed"
    finally:
        ep_repo.delete(created_ep.id)

def test_api_download_endpoint(db_session, tmp_path):
    ep_repo = EpisodeRepository(db_session)
    ep = Episode(
        title="API Download Test Episode",
        audio_url="https://audio.example.com/test_api.mp3",
        status="uploaded"
    )
    created_ep = ep_repo.create(ep)

    try:
        # Mock download_episode_audio service call
        mock_updated_ep = Episode(
            id=created_ep.id,
            title=created_ep.title,
            status="uploaded",
            audio_url="/storage/downloaded_test_api.mp3",
            file_size=102400,
        )

        with patch("backend.services.audio_downloader_service.audio_downloader_service.download_episode_audio", new_callable=AsyncMock) as mock_dl:
            mock_dl.return_value = mock_updated_ep

            resp = client.post(f"/api/episodes/{created_ep.id}/download")
            assert resp.status_code == 200
            data = resp.json()
            assert data["id"] == created_ep.id
            assert data["status"] == "uploaded"
            assert data["audio_url"] == "/storage/downloaded_test_api.mp3"
            assert data["file_size"] == 102400
    finally:
        ep_repo.delete(created_ep.id)

def test_existing_upload_endpoint_still_works():
    # Verify standard multipart form file upload remains completely operational
    audio_content = b"ID3\x03\x00\x00\x00MOCK_UPLOAD_FILE_CONTENT"
    files = {
        "file": ("podcast_test_recording.mp3", io.BytesIO(audio_content), "audio/mpeg")
    }
    data = {
        "title": "Multipart Direct Upload Episode",
        "description": "Uploaded via form",
        "language": "en"
    }

    resp = client.post("/api/episodes", data=data, files=files)
    assert resp.status_code in (200, 201)
    res_data = resp.json()
    assert res_data["title"] == "Multipart Direct Upload Episode"
    assert res_data["status"] == "queued"
    ep_id = res_data["id"]

    # Cleanup
    client.delete(f"/api/episodes/{ep_id}")
