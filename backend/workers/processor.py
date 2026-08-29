import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal
from backend.models.user import User
from backend.models.episode import Episode
from backend.models.processing_job import ProcessingJob
from backend.models.speaker import Speaker
from backend.models.transcript_segment import TranscriptSegment
from backend.models.embedding import Embedding
from backend.models.episode_insight import EpisodeInsight
from backend.models.notification import Notification
from backend.storage import storage_service
from backend.services import (
    transcription_service,
    speaker_diarization_service,
    chunking_service,
    embedding_service,
    insight_service,
)

logger = logging.getLogger("backend.workers.processor")

def ensure_default_user(db: Session) -> str:
    user = db.query(User).filter(User.id == "default-user").first()
    if not user:
        user = User(
            id="default-user",
            email="developer@example.com",
            name="Developer User",
        )
        db.add(user)
        db.flush()
    return user.id

class AudioPipelineProcessor:
    """Executes the asynchronous AI audio processing pipeline."""

    async def run(self, episode_id: str, job_id: Optional[str] = None, db: Optional[Session] = None):
        owns_session = False
        if db is None:
            db = SessionLocal()
            owns_session = True

        try:
            # Ensure user exists for foreign keys
            user_id = ensure_default_user(db)

            # 1. Fetch Episode
            episode = db.query(Episode).filter(Episode.id == episode_id).first()
            if not episode:
                logger.error(f"Episode {episode_id} not found for processing.")
                return

            # 2. Fetch or create ProcessingJob
            if job_id:
                job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
            else:
                job = db.query(ProcessingJob).filter(ProcessingJob.episode_id == episode_id).order_by(ProcessingJob.started_at.desc()).first()

            if not job:
                job = ProcessingJob(
                    episode_id=episode_id,
                    status="queued",
                    current_stage="queued",
                    progress=0,
                )
                db.add(job)
                db.flush()

            job.started_at = datetime.now(timezone.utc)
            job.status = "transcribing"
            job.current_stage = "transcribing"
            job.progress = 10
            episode.status = "transcribing"
            db.flush()

            audio_file_path = storage_service.get_file_path(episode.audio_url or "")

            # --- STAGE 1: TRANSCRIPTION ---
            logger.info(f"[{episode.id}] Stage 1: Transcribing audio...")
            raw_segments = await transcription_service.transcribe(
                audio_path=audio_file_path or "",
                title=episode.title
            )
            job.progress = 30
            db.flush()

            # --- STAGE 2: SPEAKER DETECTION ---
            logger.info(f"[{episode.id}] Stage 2: Detecting speakers...")
            job.current_stage = "speaker_detection"
            job.status = "speaker_detection"
            episode.status = "speaker_detection"
            job.progress = 40
            db.flush()

            diarized_segments, speaker_profiles = await speaker_diarization_service.diarize(
                audio_path=audio_file_path or "",
                raw_segments=raw_segments
            )

            # Persist speakers
            speaker_map = {}
            for spk_data in speaker_profiles:
                speaker = Speaker(
                    episode_id=episode.id,
                    label=spk_data["label"],
                    display_name=spk_data.get("display_name"),
                    speaking_duration=spk_data.get("duration", 0.0),
                    segment_count=spk_data.get("count", 0),
                )
                db.add(speaker)
                db.flush()
                speaker_map[speaker.label] = speaker.id

            job.progress = 55
            db.flush()

            # --- STAGE 3: CHUNKING & TRANSCRIPT PERSISTENCE ---
            logger.info(f"[{episode.id}] Stage 3: Speaker-aware chunking...")
            job.current_stage = "chunking"
            job.status = "chunking"
            episode.status = "chunking"
            job.progress = 65
            db.flush()

            max_end_time = 0.0
            created_segments = []
            for seg in diarized_segments:
                spk_id = speaker_map.get(seg.get("speaker_label"))
                segment = TranscriptSegment(
                    episode_id=episode.id,
                    speaker_id=spk_id,
                    start_time=seg["start_time"],
                    end_time=seg["end_time"],
                    text=seg["text"],
                    sequence_number=seg.get("sequence_number", 1),
                    confidence=seg.get("confidence", 0.95),
                )
                db.add(segment)
                db.flush()
                created_segments.append(segment)
                if seg["end_time"] > max_end_time:
                    max_end_time = seg["end_time"]

            # Update episode duration if previously unset
            if max_end_time > 0:
                episode.duration = max_end_time

            # Perform temporal chunking
            chunks = chunking_service.chunk(diarized_segments)
            job.progress = 75
            db.flush()

            # --- STAGE 4: EMBEDDINGS GENERATION ---
            logger.info(f"[{episode.id}] Stage 4: Generating embeddings...")
            job.current_stage = "embedding"
            job.status = "embedding"
            episode.status = "embedding"
            job.progress = 80
            db.flush()

            chunk_texts = [c["text"] for c in chunks]
            vectors = await embedding_service.embed_batch(chunk_texts)
            job.progress = 90
            db.flush()

            # --- STAGE 5: VECTOR INDEXING & INSIGHT GENERATION ---
            logger.info(f"[{episode.id}] Stage 5: Indexing vectors and insights...")
            job.current_stage = "indexing"
            job.status = "indexing"
            episode.status = "indexing"
            job.progress = 95
            db.flush()

            # Link embeddings to segments
            for i, seg in enumerate(created_segments):
                if i < len(vectors):
                    embedding_record = Embedding(
                        segment_id=seg.id,
                        embedding=vectors[i],
                    )
                    db.add(embedding_record)

            # Generate AI Episode Insights
            full_transcript = " ".join(s.text for s in created_segments)
            insight_data = await insight_service.generate_insights(episode.title, full_transcript)

            insight = EpisodeInsight(
                episode_id=episode.id,
                overview=insight_data.get("overview"),
                competencies=insight_data.get("competencies", []),
                technologies=insight_data.get("technologies", []),
                architecture=insight_data.get("architecture", []),
                resume_bullet=insight_data.get("resume_bullet"),
            )
            db.add(insight)

            # --- STAGE 6: COMPLETED ---
            now = datetime.now(timezone.utc)
            job.current_stage = "complete"
            job.status = "completed"
            job.progress = 100
            job.completed_at = now

            episode.status = "completed"
            episode.processed_at = now

            # Create notification
            notif = Notification(
                user_id=user_id,
                type="processing_complete",
                title="Processing Complete",
                description=f"Episode '{episode.title}' has been transcribed, diarized, and vector indexed.",
                link=f"/episodes/{episode.id}",
                read=False,
            )
            db.add(notif)
            if owns_session:
                db.commit()
            else:
                db.flush()
            logger.info(f"[{episode.id}] Successfully completed processing pipeline!")

        except Exception as e:
            logger.exception(f"Error processing episode {episode_id}: {str(e)}")
            try:
                job = db.query(ProcessingJob).filter(ProcessingJob.episode_id == episode_id).order_by(ProcessingJob.started_at.desc()).first()
                if job:
                    job.status = "failed"
                    job.error_message = str(e)
                    job.completed_at = datetime.now(timezone.utc)

                episode = db.query(Episode).filter(Episode.id == episode_id).first()
                if episode:
                    episode.status = "failed"

                notif = Notification(
                    user_id="default-user",
                    type="processing_failed",
                    title="Processing Failed",
                    description=f"Processing failed for episode: {str(e)}",
                    link=f"/episodes/{episode_id}",
                    read=False,
                )
                db.add(notif)
                if owns_session:
                    db.commit()
                else:
                    db.flush()
            except Exception as inner_e:
                logger.error(f"Failed to record failure state: {inner_e}")
        finally:
            if owns_session:
                db.close()

# Global pipeline instance
pipeline_processor = AudioPipelineProcessor()

def trigger_processing_background(episode_id: str, job_id: Optional[str] = None):
    """Triggers non-blocking background processing."""
    asyncio.create_task(pipeline_processor.run(episode_id, job_id))
