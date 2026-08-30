from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from backend.models.podcast import Podcast
from backend.models.episode import Episode
from backend.repositories.base_repo import BaseRepository

class PodcastRepository(BaseRepository[Podcast]):
    def __init__(self, db: Session):
        super().__init__(Podcast, db)

    def get_podcasts(
        self,
        query: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Podcast]:
        q = self.db.query(Podcast)
        if query:
            q = q.filter(
                or_(
                    Podcast.title.ilike(f"%{query}%"),
                    Podcast.description.ilike(f"%{query}%"),
                    Podcast.author.ilike(f"%{query}%"),
                    Podcast.publisher.ilike(f"%{query}%"),
                )
            )
        return q.order_by(desc(Podcast.created_at)).offset(skip).limit(limit).all()

    def get_by_feed_url(self, feed_url: str) -> Optional[Podcast]:
        """Lookup podcast by RSS feed URL for deduplication."""
        if not feed_url:
            return None
        return self.db.query(Podcast).filter(Podcast.feed_url == feed_url).first()

    def get_by_external_id(self, external_id: str) -> Optional[Podcast]:
        """Lookup podcast by external directory ID (iTunes/Spotify)."""
        if not external_id:
            return None
        return self.db.query(Podcast).filter(Podcast.external_id == external_id).first()

    def get_episodes(
        self,
        podcast_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Episode]:
        """Fetches all episodes belonging to this podcast ordered by publication date / creation date."""
        return (
            self.db.query(Episode)
            .filter(Episode.podcast_id == podcast_id)
            .order_by(desc(Episode.publication_date), desc(Episode.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
