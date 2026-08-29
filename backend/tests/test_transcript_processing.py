import pytest
from backend.services.chunking_service import SpeakerAwareChunkingService
from backend.models import Episode, Speaker, TranscriptSegment

def test_timestamp_ordering():
    chunker = SpeakerAwareChunkingService(max_chunk_duration=30.0)
    raw_segments = [
        {"speaker_label": "Speaker 1", "speaker_id": "spk-1", "start_time": 0.0, "end_time": 5.2, "text": "Segment one."},
        {"speaker_label": "Speaker 1", "speaker_id": "spk-1", "start_time": 5.2, "end_time": 12.0, "text": "Segment two."},
        {"speaker_label": "Speaker 2", "speaker_id": "spk-2", "start_time": 12.0, "end_time": 25.4, "text": "Segment three from second speaker."},
        {"speaker_label": "Speaker 1", "speaker_id": "spk-1", "start_time": 25.4, "end_time": 38.0, "text": "Back to first speaker."},
    ]

    chunks = chunker.chunk(raw_segments)
    assert len(chunks) == 3

    # Verify timestamps are strictly ordered
    for i, c in enumerate(chunks):
        assert c["start_time"] < c["end_time"]
        assert c["sequence_number"] == i + 1
        if i > 0:
            assert c["start_time"] >= chunks[i-1]["end_time"]

def test_speaker_changes():
    chunker = SpeakerAwareChunkingService(max_chunk_duration=60.0)
    raw_segments = [
        {"speaker_label": "Speaker 1", "speaker_id": "spk-1", "start_time": 0.0, "end_time": 4.0, "text": "Hello there."},
        {"speaker_label": "Speaker 2", "speaker_id": "spk-2", "start_time": 4.0, "end_time": 8.0, "text": "Hi Alex."},
        {"speaker_label": "Speaker 3", "speaker_id": "spk-3", "start_time": 8.0, "end_time": 12.0, "text": "Great to join."},
    ]

    chunks = chunker.chunk(raw_segments)
    assert len(chunks) == 3
    assert chunks[0]["speaker_label"] == "Speaker 1"
    assert chunks[1]["speaker_label"] == "Speaker 2"
    assert chunks[2]["speaker_label"] == "Speaker 3"

def test_empty_text():
    chunker = SpeakerAwareChunkingService()
    raw_segments = [
        {"speaker_label": "Speaker 1", "start_time": 0.0, "end_time": 2.0, "text": ""},
        {"speaker_label": "Speaker 1", "start_time": 2.0, "end_time": 4.0, "text": "   "},
        {"speaker_label": "Speaker 1", "start_time": 4.0, "end_time": 6.0, "text": None},
        {"speaker_label": "Speaker 1", "start_time": 6.0, "end_time": 10.0, "text": "Valid speech here."},
    ]

    chunks = chunker.chunk(raw_segments)
    assert len(chunks) == 1
    assert chunks[0]["text"] == "Valid speech here."
    assert chunks[0]["start_time"] == 6.0
    assert chunks[0]["end_time"] == 10.0

def test_short_segments_merging():
    chunker = SpeakerAwareChunkingService(max_chunk_duration=30.0)
    raw_segments = [
        {"speaker_label": "Speaker 1", "speaker_id": "spk-1", "start_time": 0.0, "end_time": 2.0, "text": "Yeah."},
        {"speaker_label": "Speaker 1", "speaker_id": "spk-1", "start_time": 2.0, "end_time": 5.0, "text": "I agree completely."},
        {"speaker_label": "Speaker 1", "speaker_id": "spk-1", "start_time": 5.0, "end_time": 12.0, "text": "That was the main architecture decision."},
    ]

    chunks = chunker.chunk(raw_segments)
    assert len(chunks) == 1
    assert chunks[0]["text"] == "Yeah. I agree completely. That was the main architecture decision."
    assert chunks[0]["start_time"] == 0.0
    assert chunks[0]["end_time"] == 12.0

def test_long_segments_splitting():
    chunker = SpeakerAwareChunkingService(max_chunk_duration=20.0)
    long_text = (
        "First sentence about distributed consensus algorithms. "
        "Second sentence explains the Paxos and Raft trade-offs in depth. "
        "Third sentence covers split-brain scenarios and leader leases. "
        "Fourth sentence provides real world production recommendations."
    )
    raw_segments = [
        {
            "speaker_label": "Speaker 1",
            "speaker_id": "spk-1",
            "start_time": 0.0,
            "end_time": 60.0, # 60s > 20s max duration
            "text": long_text,
        }
    ]

    chunks = chunker.chunk(raw_segments)
    assert len(chunks) > 1
    # Check that sentences were split cleanly
    assert all(len(c["text"]) > 0 for c in chunks)
    # Check start and end times span total range without overlap
    assert chunks[0]["start_time"] == 0.0
    assert chunks[-1]["end_time"] == 60.0

def test_transcript_and_speakers_endpoints(client, db):
    ep = Episode(id="ep-tr-test", title="Transcript Test Episode", duration=120.0, status="completed")
    spk1 = Speaker(id="spk-tr-1", episode_id=ep.id, label="Speaker 1", display_name="Alice", speaking_duration=60.0, segment_count=1)
    spk2 = Speaker(id="spk-tr-2", episode_id=ep.id, label="Speaker 2", display_name="Bob", speaking_duration=60.0, segment_count=1)
    
    seg1 = TranscriptSegment(
        id="seg-tr-1",
        episode_id=ep.id,
        speaker_id=spk1.id,
        start_time=0.0,
        end_time=60.0,
        text="Alice discusses database scaling.",
        sequence_number=1,
        confidence=0.98,
    )
    seg2 = TranscriptSegment(
        id="seg-tr-2",
        episode_id=ep.id,
        speaker_id=spk2.id,
        start_time=60.0,
        end_time=120.0,
        text="Bob explains caching strategies.",
        sequence_number=2,
        confidence=0.95,
    )
    db.add_all([ep, spk1, spk2, seg1, seg2])
    db.flush()

    # 1. GET /api/episodes/{id}/transcript
    res_tr = client.get(f"/api/episodes/{ep.id}/transcript")
    assert res_tr.status_code == 200
    segments = res_tr.json()
    assert len(segments) == 2
    assert segments[0]["startSec"] == 0.0
    assert segments[0]["start"] in ["00:00", "0:00"]
    assert segments[1]["startSec"] == 60.0
    assert segments[1]["start"] in ["01:00", "1:00"]

    # 2. GET /api/episodes/{id}/speakers
    res_spk = client.get(f"/api/episodes/{ep.id}/speakers")
    assert res_spk.status_code == 200
    speakers = res_spk.json()
    assert len(speakers) == 2
    assert any(s["display_name"] == "Alice" for s in speakers)
    assert any(s["display_name"] == "Bob" for s in speakers)
