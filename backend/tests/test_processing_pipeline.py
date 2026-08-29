import asyncio
import pytest
from unittest.mock import patch
from backend.models import User, Episode, ProcessingJob, Speaker, TranscriptSegment, Embedding, EpisodeInsight, Notification
from backend.workers.processor import AudioPipelineProcessor

def test_complete_processing_pipeline_success(db):
    user = User(id="u-proc-1", email="u-proc-1@example.com")
    episode = Episode(
        id="ep-proc-test-1",
        title="Distributed Caching Architecture",
        original_filename="caching_arch.mp3",
        audio_url="/storage/dummy.mp3",
        status="queued",
    )
    job = ProcessingJob(
        id="job-proc-test-1",
        episode_id=episode.id,
        status="queued",
        current_stage="queued",
        progress=0,
    )
    db.add_all([user, episode, job])
    db.flush()

    # Run pipeline with active test db session
    processor = AudioPipelineProcessor()
    asyncio.run(processor.run(episode_id=episode.id, job_id=job.id, db=db))

    updated_ep = db.query(Episode).filter(Episode.id == episode.id).first()
    assert updated_ep.status == "completed"
    assert updated_ep.duration > 0

    updated_job = db.query(ProcessingJob).filter(ProcessingJob.id == job.id).first()
    assert updated_job.status == "completed"
    assert updated_job.current_stage == "complete"
    assert updated_job.progress == 100
    assert updated_job.completed_at is not None

    # Verify speakers created
    speakers = db.query(Speaker).filter(Speaker.episode_id == episode.id).all()
    assert len(speakers) >= 2
    assert any(s.label == "Speaker 1" for s in speakers)

    # Verify transcript segments created
    segments = db.query(TranscriptSegment).filter(TranscriptSegment.episode_id == episode.id).all()
    assert len(segments) > 0
    assert all(s.start_time >= 0 and s.end_time > s.start_time for s in segments)

    # Verify embeddings created
    embeddings = db.query(Embedding).join(TranscriptSegment).filter(TranscriptSegment.episode_id == episode.id).all()
    assert len(embeddings) > 0

    # Verify insights created
    insight = db.query(EpisodeInsight).filter(EpisodeInsight.episode_id == episode.id).first()
    assert insight is not None
    assert len(insight.competencies) > 0

    # Verify notification created
    notif = db.query(Notification).filter(Notification.type == "processing_complete").first()
    assert notif is not None

def test_processing_pipeline_error_handling(db):
    episode = Episode(
        id="ep-fail-test",
        title="Corrupted Podcast Audio",
        status="queued",
    )
    job = ProcessingJob(
        id="job-fail-test",
        episode_id=episode.id,
        status="queued",
        current_stage="queued",
        progress=0,
    )
    db.add_all([episode, job])
    db.flush()

    # Mock transcription failure
    processor = AudioPipelineProcessor()
    with patch("backend.workers.processor.transcription_service.transcribe", side_effect=ValueError("Audio codec header corrupted")):
        asyncio.run(processor.run(episode_id=episode.id, job_id=job.id, db=db))

    failed_ep = db.query(Episode).filter(Episode.id == episode.id).first()
    assert failed_ep.status == "failed"

    failed_job = db.query(ProcessingJob).filter(ProcessingJob.id == job.id).first()
    assert failed_job.status == "failed"
    assert "Audio codec header corrupted" in failed_job.error_message

def test_get_episode_processing_endpoints(client, db):
    episode = Episode(id="ep-status-test", title="Status Check Episode", status="transcribing")
    job = ProcessingJob(
        id="job-status-test",
        episode_id=episode.id,
        status="transcribing",
        current_stage="transcribing",
        progress=30,
    )
    db.add_all([episode, job])
    db.flush()

    # 1. GET /api/episodes/{id}/processing
    res = client.get(f"/api/episodes/{episode.id}/processing")
    assert res.status_code == 200
    data = res.json()
    assert data["episode_id"] == episode.id
    assert data["status"] == "transcribing"
    assert data["progress"] == 30

    # 2. GET /api/processing/jobs
    res_jobs = client.get("/api/processing/jobs")
    assert res_jobs.status_code == 200
    jobs_list = res_jobs.json()
    assert any(j["id"] == "job-status-test" for j in jobs_list)

    # 3. GET /api/processing/stats
    res_stats = client.get("/api/processing/stats")
    assert res_stats.status_code == 200
    assert "active_jobs_count" in res_stats.json()

def test_processing_retry_and_cancel_endpoints(client, db):
    episode = Episode(id="ep-act-test", title="Actions Episode", status="processing")
    job = ProcessingJob(
        id="job-act-test",
        episode_id=episode.id,
        status="processing",
        current_stage="transcribing",
        progress=25,
    )
    db.add_all([episode, job])
    db.flush()

    # Cancel job
    res_cancel = client.post(f"/api/processing/jobs/{job.id}/cancel")
    assert res_cancel.status_code == 200
    assert res_cancel.json()["status"] == "failed"

    # Retry job
    res_retry = client.post(f"/api/processing/jobs/{job.id}/retry")
    assert res_retry.status_code == 200
    assert res_retry.json()["status"] == "queued"
