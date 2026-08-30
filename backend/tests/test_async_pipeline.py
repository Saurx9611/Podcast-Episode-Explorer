import pytest
import asyncio
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.main import app
from backend.core.database import SessionLocal, init_db
from backend.models.episode import Episode
from backend.models.processing_job import ProcessingJob
from backend.models.speaker import Speaker
from backend.models.transcript_segment import TranscriptSegment
from backend.models.embedding import Embedding
from backend.models.episode_insight import EpisodeInsight
from backend.repositories.episode_repo import EpisodeRepository
from backend.repositories.processing_repo import ProcessingRepository
from backend.workers.processor import AudioPipelineProcessor, pipeline_processor

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

@pytest.mark.anyio
async def test_full_end_to_end_async_pipeline(db_session):
    ep_repo = EpisodeRepository(db_session)
    proc_repo = ProcessingRepository(db_session)

    # 1. Create episode
    ep = Episode(
        title="Async Pipeline Full Flow",
        status="queued",
        audio_url="/storage/test_audio.mp3",
    )
    created_ep = ep_repo.create(ep)

    # 2. Create job
    job = ProcessingJob(
        episode_id=created_ep.id,
        status="queued",
        current_stage="queued",
        progress=0,
    )
    created_job = proc_repo.create(job)

    try:
        # 3. Execute Pipeline
        processor = AudioPipelineProcessor()
        await processor.run(episode_id=created_ep.id, job_id=created_job.id, db=db_session)

        # 4. Verify Episode status
        db_session.refresh(created_ep)
        assert created_ep.status == "completed"
        assert created_ep.processed_at is not None
        assert created_ep.duration > 0

        # 5. Verify ProcessingJob status
        db_session.refresh(created_job)
        assert created_job.status == "completed"
        assert created_job.current_stage == "complete"
        assert created_job.progress == 100
        assert created_job.completed_at is not None

        # 6. Verify Speakers
        speakers = ep_repo.get_speakers(created_ep.id)
        assert len(speakers) >= 2

        # 7. Verify Transcript Segments
        segments = ep_repo.get_transcript(created_ep.id)
        assert len(segments) > 0
        for s in segments:
            assert s.speaker_id is not None
            assert s.start_time is not None
            assert s.end_time >= s.start_time

        # 8. Verify Embeddings
        seg_ids = [s.id for s in segments]
        embeddings = db_session.query(Embedding).filter(Embedding.segment_id.in_(seg_ids)).all()
        assert len(embeddings) > 0

        # 9. Verify Insights
        insight = ep_repo.get_insights(created_ep.id)
        assert insight is not None
        assert len(insight.overview) > 10
        assert len(insight.competencies) >= 3
        assert len(insight.technologies) >= 3

    finally:
        ep_repo.delete(created_ep.id)

@pytest.mark.anyio
async def test_idempotent_retry_no_duplicate_records(db_session):
    ep_repo = EpisodeRepository(db_session)
    proc_repo = ProcessingRepository(db_session)

    ep = Episode(
        title="Idempotency Test Episode",
        status="queued",
        audio_url="/storage/test_retry.mp3",
    )
    created_ep = ep_repo.create(ep)
    job = ProcessingJob(
        episode_id=created_ep.id,
        status="queued",
        current_stage="queued",
        progress=0,
    )
    created_job = proc_repo.create(job)

    try:
        processor = AudioPipelineProcessor()

        # Run 1
        await processor.run(episode_id=created_ep.id, job_id=created_job.id, db=db_session)
        speakers_run1 = ep_repo.get_speakers(created_ep.id)
        segments_run1 = ep_repo.get_transcript(created_ep.id)
        insights_run1 = ep_repo.get_insights(created_ep.id)

        count_speakers_1 = len(speakers_run1)
        count_segments_1 = len(segments_run1)

        # Run 2 (Simulating a Retry on the same episode)
        await processor.run(episode_id=created_ep.id, job_id=created_job.id, db=db_session)
        speakers_run2 = ep_repo.get_speakers(created_ep.id)
        segments_run2 = ep_repo.get_transcript(created_ep.id)
        insights_run2 = ep_repo.get_insights(created_ep.id)

        # Counts must NOT double; must remain exactly the same due to idempotent cleanup
        assert len(speakers_run2) == count_speakers_1
        assert len(segments_run2) == count_segments_1
        assert insights_run2 is not None

    finally:
        ep_repo.delete(created_ep.id)

@pytest.mark.anyio
async def test_pipeline_failure_recording(db_session):
    ep_repo = EpisodeRepository(db_session)
    proc_repo = ProcessingRepository(db_session)

    ep = Episode(
        title="Failing Episode Test",
        status="queued",
        audio_url="/storage/bad_audio.mp3",
    )
    created_ep = ep_repo.create(ep)
    job = ProcessingJob(
        episode_id=created_ep.id,
        status="queued",
        current_stage="queued",
        progress=0,
    )
    created_job = proc_repo.create(job)

    try:
        processor = AudioPipelineProcessor()
        # Simulate an unexpected error in transcription
        with patch("backend.workers.processor.transcription_service.transcribe", side_effect=RuntimeError("Audio decoding error at frame 400")):
            await processor.run(episode_id=created_ep.id, job_id=created_job.id, db=db_session)

        db_session.refresh(created_ep)
        db_session.refresh(created_job)

        assert created_ep.status == "failed"
        assert created_job.status == "failed"
        assert "Audio decoding error" in (created_job.error_message or "")

    finally:
        ep_repo.delete(created_ep.id)

def test_api_processing_routes(db_session):
    ep_repo = EpisodeRepository(db_session)
    proc_repo = ProcessingRepository(db_session)

    ep = Episode(title="API Processing Test", status="queued")
    created_ep = ep_repo.create(ep)
    job = ProcessingJob(
        episode_id=created_ep.id,
        status="transcribing",
        current_stage="transcribing",
        progress=25,
    )
    created_job = proc_repo.create(job)

    try:
        # 1. GET /api/processing/jobs
        res = client.get("/api/processing/jobs")
        assert res.status_code == 200
        jobs = res.json()
        assert any(j["id"] == created_job.id for j in jobs)

        # 2. GET /api/processing/stats
        stats_res = client.get("/api/processing/stats")
        assert stats_res.status_code == 200
        assert "active_jobs_count" in stats_res.json()

        # 3. POST /api/processing/jobs/{id}/cancel
        cancel_res = client.post(f"/api/processing/jobs/{created_job.id}/cancel")
        assert cancel_res.status_code == 200
        assert cancel_res.json()["status"] == "failed"
        assert cancel_res.json()["error_message"] == "Cancelled by user"

        # 4. POST /api/processing/jobs/{id}/retry
        retry_res = client.post(f"/api/processing/jobs/{created_job.id}/retry")
        assert retry_res.status_code == 200
        assert retry_res.json()["status"] == "queued"

    finally:
        ep_repo.delete(created_ep.id)
