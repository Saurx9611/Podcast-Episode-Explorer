import os
import math
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from backend.core.database import SessionLocal, init_db
from backend.models.episode import Episode
from backend.models.processing_job import ProcessingJob
from backend.models.transcript_segment import TranscriptSegment
from backend.repositories.episode_repo import EpisodeRepository
from backend.services.transcription_service import MockTranscriptionService, get_transcription_service
from backend.services.whisper_transcription_service import FasterWhisperTranscriptionService
from backend.core.exceptions import ValidationException
from backend.workers.processor import AudioPipelineProcessor

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

def test_transcription_provider_factory():
    # 1. Test explicit mock provider
    mock_svc = get_transcription_service("mock")
    assert isinstance(mock_svc, MockTranscriptionService)

    # 2. Test explicit whisper provider
    whisper_svc = get_transcription_service("faster_whisper")
    assert isinstance(whisper_svc, FasterWhisperTranscriptionService)

    whisper_svc_alias = get_transcription_service("whisper")
    assert isinstance(whisper_svc_alias, FasterWhisperTranscriptionService)

@pytest.mark.anyio
async def test_mock_transcription_service_segments():
    svc = MockTranscriptionService()
    segments = await svc.transcribe("dummy/path.mp3", title="Distributed Systems")

    assert len(segments) >= 5
    for idx, seg in enumerate(segments):
        assert "text" in seg and len(seg["text"]) > 0
        assert "start_time" in seg and "end_time" in seg
        assert seg["start_time"] >= 0.0
        assert seg["end_time"] > seg["start_time"]
        assert 0.0 <= seg["confidence"] <= 1.0
        if idx > 0:
            assert seg["start_time"] >= segments[idx - 1]["start_time"]

@pytest.mark.anyio
async def test_faster_whisper_service_validation(tmp_path):
    svc = FasterWhisperTranscriptionService(model_size="tiny", device="cpu")

    # 1. Missing path
    with pytest.raises(ValidationException, match="missing"):
        await svc.transcribe("")

    # 2. Non-existent path
    with pytest.raises(ValidationException, match="does not exist"):
        await svc.transcribe(str(tmp_path / "non_existent_file.mp3"))

    # 3. Empty 0-byte file
    empty_file = tmp_path / "empty.mp3"
    empty_file.write_bytes(b"")
    with pytest.raises(ValidationException, match="empty"):
        await svc.transcribe(str(empty_file))

@pytest.mark.anyio
async def test_faster_whisper_mocked_inference(tmp_path):
    svc = FasterWhisperTranscriptionService(model_size="base", device="cpu")

    # Create dummy non-empty audio file
    fake_audio = tmp_path / "sample_audio.mp3"
    fake_audio.write_bytes(b"FAKE_AUDIO_DATA_FOR_WHISPER_INFERENCE")

    # Mock WhisperModel segment objects
    seg1 = MagicMock()
    seg1.text = "Hello and welcome to the future of AI engineering."
    seg1.start = 0.0
    seg1.end = 4.5
    seg1.avg_logprob = -0.15

    seg2 = MagicMock()
    seg2.text = "Today we discuss speech recognition and transformer architectures."
    seg2.start = 4.5
    seg2.end = 9.8
    seg2.avg_logprob = -0.05

    mock_model = MagicMock()
    mock_model.transcribe.return_value = ([seg1, seg2], MagicMock())

    with patch.object(svc, "_get_model", return_value=mock_model):
        results = await svc.transcribe(str(fake_audio), title="AI Engineering")

    assert len(results) == 2
    assert results[0]["text"] == "Hello and welcome to the future of AI engineering."
    assert results[0]["start_time"] == 0.0
    assert results[0]["end_time"] == 4.5
    assert 0.8 <= results[0]["confidence"] <= 1.0

    assert results[1]["text"] == "Today we discuss speech recognition and transformer architectures."
    assert results[1]["start_time"] == 4.5
    assert results[1]["end_time"] == 9.8

@pytest.mark.anyio
async def test_pipeline_transcription_persistence(db_session):
    ep_repo = EpisodeRepository(db_session)
    ep = Episode(
        title="Transcription Pipeline Test",
        audio_url="/storage/test.mp3",
        status="uploaded"
    )
    created_ep = ep_repo.create(ep)

    try:
        processor = AudioPipelineProcessor()
        await processor.run(episode_id=created_ep.id, db=db_session)

        # Verify episode state
        updated_ep = ep_repo.get_by_id(created_ep.id)
        assert updated_ep.status == "completed"
        assert updated_ep.duration > 0

        # Verify segments in database
        segments = ep_repo.get_transcript(created_ep.id)
        assert len(segments) > 0
        for seg in segments:
            assert seg.episode_id == created_ep.id
            assert seg.text is not None
            assert seg.start_time is not None
            assert seg.end_time > seg.start_time
            assert seg.confidence is not None
    finally:
        ep_repo.delete(created_ep.id)
