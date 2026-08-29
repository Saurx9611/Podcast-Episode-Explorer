import os
import sys
from datetime import datetime
import uuid

# Add the project root to sys.path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import SessionLocal, Base, engine
from backend.models import User, Project, Episode, Speaker, TranscriptSegment, Embedding, ProcessingJob, SavedSearch, Notification, EpisodeInsight

# This will create tables if Alembic hasn't
Base.metadata.create_all(bind=engine)

def seed_db():
    db = SessionLocal()
    
    # 1. User
    user = db.query(User).filter(User.id == "dev-user-id").first()
    if not user:
        user = User(id="dev-user-id", email="dev@example.com", name="Developer")
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2. Projects
    if db.query(Project).count() == 0:
        p1 = Project(user_id=user.id, name="Engineering Podcast", description="Technical deep dives")
        p2 = Project(user_id=user.id, name="AI Infrastructure", description="Building scalable AI systems")
        db.add_all([p1, p2])
        db.commit()

        # 3. Episodes
        e1 = Episode(
            project_id=p1.id, 
            title="Scaling Distributed Systems", 
            description="An in-depth technical discussion...",
            duration=2722,
            status="completed"
        )
        db.add(e1)
        db.commit()
        
        # 4. Speakers
        s1 = Speaker(episode_id=e1.id, label="Speaker 1", display_name="Alex Morgan")
        s2 = Speaker(episode_id=e1.id, label="Speaker 2", display_name="Priya Shah")
        db.add_all([s1, s2])
        db.commit()

        # 5. Transcript Segments & Embeddings
        ts1 = TranscriptSegment(
            episode_id=e1.id, speaker_id=s1.id, start_time=0.0, end_time=15.5,
            text="Welcome to the Engineering Podcast.", sequence_number=1
        )
        db.add(ts1)
        db.commit()

        emb1 = Embedding(segment_id=ts1.id, embedding=[0.0] * 1536)
        db.add(emb1)
        db.commit()

        # 6. Processing Job
        job = ProcessingJob(episode_id=e1.id, status="completed", current_stage="complete", progress=100)
        db.add(job)
        
        # 7. Saved Search
        ss1 = SavedSearch(user_id=user.id, name="Database Bottlenecks", query="database scaling issues")
        db.add(ss1)
        
        # 8. Notification
        n1 = Notification(user_id=user.id, type="processing_complete", title="Processing completed", description="Scaling Distributed Systems is ready.")
        db.add(n1)

        db.commit()
        print("Database successfully seeded.")
    else:
        print("Database already has data. Skipping seed.")

    db.close()

if __name__ == "__main__":
    seed_db()
