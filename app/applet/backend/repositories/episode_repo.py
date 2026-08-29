from sqlalchemy.orm import Session
from backend.models import Episode, TranscriptSegment, Speaker, EpisodeInsight
from typing import List, Optional

class EpisodeRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create_episode(self, episode: Episode) -> Episode:
        self.db.add(episode)
        self.db.commit()
        self.db.refresh(episode)
        return episode
        
    def get_episode(self, episode_id: str) -> Optional[Episode]:
        return self.db.query(Episode).filter(Episode.id == episode_id).first()
        
    def get_episodes(self, skip: int = 0, limit: int = 100) -> List[Episode]:
        return self.db.query(Episode).offset(skip).limit(limit).all()
        
    def delete_episode(self, episode_id: str) -> bool:
        episode = self.get_episode(episode_id)
        if episode:
            self.db.delete(episode)
            self.db.commit()
            return True
        return False
        
    def get_transcript(self, episode_id: str) -> List[TranscriptSegment]:
        return self.db.query(TranscriptSegment).filter(
            TranscriptSegment.episode_id == episode_id
        ).order_by(TranscriptSegment.sequence_number).all()
        
    def get_speakers(self, episode_id: str) -> List[Speaker]:
        return self.db.query(Speaker).filter(Speaker.episode_id == episode_id).all()
        
    def get_insights(self, episode_id: str) -> Optional[EpisodeInsight]:
        return self.db.query(EpisodeInsight).filter(EpisodeInsight.episode_id == episode_id).first()
