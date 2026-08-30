import os
import uuid
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from backend.main import app
from backend.core.database import SessionLocal, init_db
from backend.models.podcast import Podcast
from backend.models.episode import Episode
from backend.repositories.podcast_repo import PodcastRepository
from backend.repositories.episode_repo import EpisodeRepository
from backend.storage.local_storage import LocalStorageService, LocalAudioStorage

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

def test_podcast_crud(db_session):
    repo = PodcastRepository(db_session)
    unique_feed = f"https://lexfridman.com/feed/podcast_{uuid.uuid4().hex[:8]}/"
    
    # 1. Create
    podcast = Podcast(
        title="Lex Fridman Podcast",
        description="Conversations about AI, science, technology, and philosophy.",
        author="Lex Fridman",
        feed_url=unique_feed,
        artwork_url="https://lexfridman.com/art.jpg",
        language="en"
    )
    created = repo.create(podcast)
    assert created.id is not None
    assert created.title == "Lex Fridman Podcast"

    try:
        # 2. Read by ID and Feed URL
        fetched = repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.author == "Lex Fridman"

        by_feed = repo.get_by_feed_url(unique_feed)
        assert by_feed is not None
        assert by_feed.id == created.id

        # 3. Update
        fetched.publisher = "Lex Media"
        updated = repo.update(fetched)
        assert updated.publisher == "Lex Media"
    finally:
        # 4. Delete
        repo.delete(created.id)
        assert repo.get_by_id(created.id) is None

def test_episode_podcast_relationship_and_deduplication(db_session):
    pod_repo = PodcastRepository(db_session)
    ep_repo = EpisodeRepository(db_session)

    unique_feed = f"https://latentspace.podbean.com/feed_{uuid.uuid4().hex[:8]}.xml"
    podcast = Podcast(
        title="Latent Space",
        description="The AI Engineer Podcast",
        author="Swyx & Alessio",
        feed_url=unique_feed,
    )
    podcast = pod_repo.create(podcast)

    try:
        # Create episode with GUID & metadata
        guid_val = f"latent-space-ep-{uuid.uuid4().hex[:8]}"
        audio_url_val = f"https://audio.latentspace.com/{uuid.uuid4().hex[:8]}.mp3"
        ep = Episode(
            podcast_id=podcast.id,
            guid=guid_val,
            title="Building AI Agents with PyTorch",
            description="Deep dive into agent tool calling.",
            publication_date=datetime.now(timezone.utc),
            episode_number=42,
            season_number=2,
            audio_url=audio_url_val,
            duration=3600.0,
            status="completed"
        )
        created_ep = ep_repo.create(ep)
        assert created_ep.podcast_id == podcast.id
        assert created_ep.guid == guid_val

        # Test Deduplication lookup by GUID
        dup_match = ep_repo.get_by_guid(podcast.id, guid_val)
        assert dup_match is not None
        assert dup_match.id == created_ep.id

        # Test Deduplication lookup by Audio URL / Title
        dup_by_url = ep_repo.get_by_audio_url_or_title(podcast.id, audio_url_val, "Wrong Title")
        assert dup_by_url is not None
        assert dup_by_url.id == created_ep.id

        # Test Non-duplicate lookup returns None
        assert ep_repo.get_by_guid(podcast.id, "non-existent-guid") is None

        # Test podcast.episodes relationship
        pod_episodes = pod_repo.get_episodes(podcast.id)
        assert len(pod_episodes) >= 1
        assert pod_episodes[0].guid == guid_val
    finally:
        # Cleanup
        pod_repo.delete(podcast.id)

def test_storage_abstraction_bytes_and_files(tmp_path):
    storage = LocalStorageService(storage_dir=str(tmp_path))
    
    # 1. Test save_bytes (simulating RSS audio downloader)
    raw_audio = b"ID3\x03\x00\x00\x00\x00\x00\x10MOCK_AUDIO_DATA_PAYLOAD_FOR_TESTING"
    url, filename, size, mime = storage.save_bytes(raw_audio, "downloaded_episode.mp3", "audio/mpeg")
    
    assert url.startswith("/storage/")
    assert "downloaded_episode.mp3" in filename
    assert size == len(raw_audio)
    assert mime == "audio/mpeg"
    assert storage.file_exists(url) is True
    
    local_path = storage.get_file_path(url)
    assert os.path.exists(local_path)

    # 2. Test delete_file
    deleted = storage.delete_file(url)
    assert deleted is True
    assert storage.file_exists(url) is False

def test_podcast_api_endpoints():
    unique_feed = f"https://hubermanlab.com/feed_{uuid.uuid4().hex[:8]}"
    
    # 1. Create via API
    resp = client.post("/api/podcasts", json={
        "title": "Huberman Lab",
        "description": "Science and science-based tools for everyday life.",
        "author": "Dr. Andrew Huberman",
        "feed_url": unique_feed
    })
    assert resp.status_code == 201
    data = resp.json()
    pod_id = data["id"]
    assert data["title"] == "Huberman Lab"

    # 2. List
    list_resp = client.get("/api/podcasts")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert any(p["id"] == pod_id for p in items)

    # 3. Get Detail
    detail_resp = client.get(f"/api/podcasts/{pod_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["author"] == "Dr. Andrew Huberman"

    # 4. Get Episodes for Podcast
    eps_resp = client.get(f"/api/podcasts/{pod_id}/episodes")
    assert eps_resp.status_code == 200
    assert isinstance(eps_resp.json(), list)

    # 5. Delete
    del_resp = client.delete(f"/api/podcasts/{pod_id}")
    assert del_resp.status_code == 200
    assert client.get(f"/api/podcasts/{pod_id}").status_code == 404
