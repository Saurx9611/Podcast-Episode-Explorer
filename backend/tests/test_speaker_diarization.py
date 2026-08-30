import pytest
from unittest.mock import patch, MagicMock

from backend.core.database import SessionLocal, init_db
from backend.models.episode import Episode
from backend.models.speaker import Speaker
from backend.models.transcript_segment import TranscriptSegment
from backend.repositories.episode_repo import EpisodeRepository
from backend.services.speaker_diarization_service import (
    MockSpeakerDiarizationService,
    get_speaker_diarization_service,
)
from backend.services.pyannote_diarization_service import (
    AcousticSpeakerDiarizationService,
    PyannoteSpeakerDiarizationService,
    align_transcript_with_speakers,
)
from backend.services.chunking_service import SpeakerAwareChunkingService
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

def test_diarization_provider_factory():
    mock_svc = get_speaker_diarization_service("mock")
    assert isinstance(mock_svc, MockSpeakerDiarizationService)

    acoustic_svc = get_speaker_diarization_service("acoustic")
    assert isinstance(acoustic_svc, AcousticSpeakerDiarizationService)

    pyannote_svc = get_speaker_diarization_service("pyannote")
    assert isinstance(pyannote_svc, PyannoteSpeakerDiarizationService)

def test_align_transcript_with_speakers():
    raw_segments = [
        {"start_time": 0.0, "end_time": 10.0, "text": "Welcome to the podcast.", "confidence": 0.98},
        {"start_time": 10.5, "end_time": 25.0, "text": "Thanks for having me on.", "confidence": 0.95},
        {"start_time": 25.2, "end_time": 40.0, "text": "Let's dive into distributed consensus.", "confidence": 0.97},
        {"start_time": 41.0, "end_time": 60.0, "text": "Consensus is critical for reliability.", "confidence": 0.94},
    ]

    speaker_turns = [
        {"start": 0.0, "end": 10.2, "speaker": "HOST_TRACK"},
        {"start": 10.3, "end": 25.1, "speaker": "GUEST_A_TRACK"},
        {"start": 25.1, "end": 40.5, "speaker": "HOST_TRACK"},
        {"start": 40.8, "end": 60.0, "speaker": "GUEST_B_TRACK"},
    ]

    diarized, profiles = align_transcript_with_speakers(raw_segments, speaker_turns)

    assert len(diarized) == 4
    # Check normalized naming
    assert diarized[0]["speaker_label"] == "Speaker 1"
    assert diarized[1]["speaker_label"] == "Speaker 2"
    assert diarized[2]["speaker_label"] == "Speaker 1"
    assert diarized[3]["speaker_label"] == "Speaker 3"

    # Verify profiles
    assert len(profiles) == 3
    spk1_prof = next(p for p in profiles if p["label"] == "Speaker 1")
    assert spk1_prof["segment_count"] == 2
    assert spk1_prof["speaking_duration"] == round(10.0 + (40.0 - 25.2), 2)

    spk2_prof = next(p for p in profiles if p["label"] == "Speaker 2")
    assert spk2_prof["segment_count"] == 1
    assert spk2_prof["speaking_duration"] == round(25.0 - 10.5, 2)

def test_overlapping_and_gap_speaker_attribution():
    raw_segments = [
        {"start_time": 5.0, "end_time": 15.0, "text": "Overlapping speech utterance", "confidence": 0.9},
        {"start_time": 50.0, "end_time": 55.0, "text": "Utterance during silence gap", "confidence": 0.9},
    ]

    # Speaker 1 covers 5.0 to 12.0 (7s overlap), Speaker 2 covers 12.0 to 15.0 (3s overlap) -> Speaker 1 wins
    speaker_turns = [
        {"start": 0.0, "end": 12.0, "speaker": "SPK_X"},
        {"start": 12.0, "end": 20.0, "speaker": "SPK_Y"},
    ]

    diarized, profiles = align_transcript_with_speakers(raw_segments, speaker_turns)
    assert diarized[0]["speaker_label"] == "Speaker 1"
    # Gap segment at 50.0 gets attributed to closest speaker (Speaker 2 / SPK_Y at 20.0)
    assert diarized[1]["speaker_label"] == "Speaker 2"

@pytest.mark.anyio
async def test_acoustic_diarization_service():
    svc = AcousticSpeakerDiarizationService()
    raw_segments = [
        {"start_time": 0.0, "end_time": 5.0, "text": "Segment 1"},
        {"start_time": 5.1, "end_time": 10.0, "text": "Segment 2"},
        {"start_time": 12.5, "end_time": 18.0, "text": "Segment 3 after long pause"},
    ]

    diarized, profiles = await svc.diarize("dummy.mp3", raw_segments)
    assert len(diarized) == 3
    assert len(profiles) >= 1
    for seg in diarized:
        assert "speaker_label" in seg
        assert seg["speaker_label"].startswith("Speaker ")

def test_speaker_aware_chunking_boundaries():
    chunker = SpeakerAwareChunkingService(max_chunk_duration=30.0)

    segments = [
        {"speaker_label": "Speaker 1", "speaker_id": "spk-1", "start_time": 0.0, "end_time": 5.0, "text": "Hello world."},
        {"speaker_label": "Speaker 1", "speaker_id": "spk-1", "start_time": 5.0, "end_time": 10.0, "text": "We love AI."},
        # Speaker change -> must break chunk boundary immediately
        {"speaker_label": "Speaker 2", "speaker_id": "spk-2", "start_time": 10.0, "end_time": 15.0, "text": "Indeed we do."},
        {"speaker_label": "Speaker 2", "speaker_id": "spk-2", "start_time": 15.0, "end_time": 20.0, "text": "It is transforming technology."},
    ]

    chunks = chunker.chunk(segments)
    assert len(chunks) == 2

    # Chunk 1: Speaker 1
    assert chunks[0]["speaker_label"] == "Speaker 1"
    assert chunks[0]["speaker_id"] == "spk-1"
    assert chunks[0]["start_time"] == 0.0
    assert chunks[0]["end_time"] == 10.0
    assert chunks[0]["text"] == "Hello world. We love AI."
    assert chunks[0]["sequence_number"] == 1

    # Chunk 2: Speaker 2
    assert chunks[1]["speaker_label"] == "Speaker 2"
    assert chunks[1]["speaker_id"] == "spk-2"
    assert chunks[1]["start_time"] == 10.0
    assert chunks[1]["end_time"] == 20.0
    assert chunks[1]["text"] == "Indeed we do. It is transforming technology."
    assert chunks[1]["sequence_number"] == 2

@pytest.mark.anyio
async def test_full_pipeline_speaker_relationship_persistence(db_session):
    ep_repo = EpisodeRepository(db_session)
    ep = Episode(
        title="Diarization Pipeline Test",
        audio_url="/storage/test_diar.mp3",
        status="uploaded"
    )
    created_ep = ep_repo.create(ep)

    try:
        processor = AudioPipelineProcessor()
        await processor.run(episode_id=created_ep.id, db=db_session)

        # Verify speakers persisted in DB
        speakers = ep_repo.get_speakers(created_ep.id)
        assert len(speakers) >= 2
        for spk in speakers:
            assert spk.episode_id == created_ep.id
            assert spk.label in ("Speaker 1", "Speaker 2", "Speaker 3")
            assert spk.speaking_duration > 0
            assert spk.segment_count > 0

        # Verify transcript segments in DB are linked to Speaker IDs
        segments = ep_repo.get_transcript(created_ep.id)
        assert len(segments) > 0
        speaker_ids = {s.id for s in speakers}
        for seg in segments:
            assert seg.speaker_id is not None
            assert seg.speaker_id in speaker_ids
    finally:
        ep_repo.delete(created_ep.id)
