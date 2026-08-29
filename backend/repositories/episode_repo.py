from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from backend.models.episode import Episode
from backend.models.speaker import Speaker
from backend.models.transcript_segment import TranscriptSegment
from backend.models.episode_insight import EpisodeInsight
from backend.repositories.base_repo import BaseRepository

class EpisodeRepository(BaseRepository[Episode]):
    def __init__(self, db: Session):
        super().__init__(Episode, db)

    def get_episodes(
        self,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        query: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Episode]:
        q = self.db.query(Episode)
        if project_id:
            q = q.filter(Episode.project_id == project_id)
        if status and status.lower() != "all":
            q = q.filter(Episode.status.ilike(status))
        if query:
            q = q.filter(
                or_(
                    Episode.title.ilike(f"%{query}%"),
                    Episode.description.ilike(f"%{query}%"),
                )
            )
        return q.order_by(desc(Episode.created_at)).offset(skip).limit(limit).all()

    def get_transcript(self, episode_id: str) -> List[TranscriptSegment]:
        return (
            self.db.query(TranscriptSegment)
            .filter(TranscriptSegment.episode_id == episode_id)
            .order_by(TranscriptSegment.sequence_number.asc())
            .all()
        )

    def get_speakers(self, episode_id: str) -> List[Speaker]:
        return (
            self.db.query(Speaker)
            .filter(Speaker.episode_id == episode_id)
            .order_by(Speaker.label.asc())
            .all()
        )

    def get_speaker_by_id(self, speaker_id: str) -> Optional[Speaker]:
        return self.db.query(Speaker).filter(Speaker.id == speaker_id).first()

    def update_speaker(self, speaker_id: str, display_name: Optional[str] = None, label: Optional[str] = None) -> Optional[Speaker]:
        speaker = self.get_speaker_by_id(speaker_id)
        if not speaker:
            return None
        if display_name is not None:
            speaker.display_name = display_name
        if label is not None:
            speaker.label = label
        self.db.commit()
        self.db.refresh(speaker)
        return speaker

    def get_insights(self, episode_id: str) -> Optional[EpisodeInsight]:
        return self.db.query(EpisodeInsight).filter(EpisodeInsight.episode_id == episode_id).first()

    def upsert_insights(
        self,
        episode_id: str,
        overview: Optional[str] = None,
        competencies: Optional[List[str]] = None,
        technologies: Optional[List[str]] = None,
        architecture: Optional[List[str]] = None,
        resume_bullet: Optional[str] = None,
    ) -> EpisodeInsight:
        insight = self.get_insights(episode_id)
        if not insight:
            insight = EpisodeInsight(
                episode_id=episode_id,
                overview=overview,
                competencies=competencies or [],
                technologies=technologies or [],
                architecture=architecture or [],
                resume_bullet=resume_bullet,
            )
            self.db.add(insight)
        else:
            if overview is not None:
                insight.overview = overview
            if competencies is not None:
                insight.competencies = competencies
            if technologies is not None:
                insight.technologies = technologies
            if architecture is not None:
                insight.architecture = architecture
            if resume_bullet is not None:
                insight.resume_bullet = resume_bullet
        self.db.commit()
        self.db.refresh(insight)
        return insight
