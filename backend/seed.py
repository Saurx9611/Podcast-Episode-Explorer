import os
import sys
from datetime import datetime, timedelta, timezone

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import SessionLocal, Base, engine
from backend.models import (
    User, Project, Episode, Speaker, TranscriptSegment,
    Embedding, ProcessingJob, SavedSearch, Notification, EpisodeInsight
)

def utc_now():
    return datetime.now(timezone.utc)

def seed_db():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        existing_user = db.query(User).filter(User.id == "dev-user-id").first()
        if existing_user:
            print("Database already contains seed data. Updating/ensuring records exist...")

        # 1. Seed User
        if not existing_user:
            user = User(
                id="dev-user-id",
                email="jane@example.com",
                name="Jane Doe",
                role="Engineer",
                preferences={
                    "playback_speed": "1.0x",
                    "chunk_duration": 45,
                    "overlap": 10,
                    "transcription_model": "Whisper Large v3",
                    "similarity_threshold": 0.70,
                    "language": "English",
                    "timezone": "Asia/Kolkata (GMT+5:30)",
                }
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            user = existing_user

        # 2. Seed Projects
        if db.query(Project).count() == 0:
            p1 = Project(
                id="proj-1",
                user_id=user.id,
                name="Engineering Podcasts",
                description="Deep dives into system design, architecture, and scaling large applications."
            )
            p2 = Project(
                id="proj-2",
                user_id=user.id,
                name="AI Research",
                description="Latest research papers, LLM advancements, and AI product development discussions."
            )
            p3 = Project(
                id="proj-3",
                user_id=user.id,
                name="Founder Interviews",
                description="Conversations with startup founders on growth, hiring, and product-market fit."
            )
            p4 = Project(
                id="proj-4",
                user_id=user.id,
                name="System Design",
                description="Mock interviews and specific case studies on system architecture."
            )
            db.add_all([p1, p2, p3, p4])
            db.commit()
        else:
            p1 = db.query(Project).filter(Project.id == "proj-1").first()
            p2 = db.query(Project).filter(Project.id == "proj-2").first()
            p3 = db.query(Project).filter(Project.id == "proj-3").first()
            p4 = db.query(Project).filter(Project.id == "proj-4").first()

        # 3. Seed Episodes
        if db.query(Episode).count() == 0:
            e1 = Episode(
                id="ep-001",
                project_id=p1.id if p1 else None,
                title="Scaling Distributed Systems",
                description="An in-depth technical discussion on the challenges and patterns for scaling distributed microservice architectures, dealing with state consistency, and migrating away from monolithic databases. Features real-world war stories from production outages.",
                original_filename="scaling_distributed_systems.mp3",
                audio_url="/mock/storage/scaling_distributed_systems.mp3",
                file_size=44879052, # 42.8 MB
                mime_type="audio/mpeg",
                duration=2722.0, # 45:22
                status="completed",
                processing_model="Whisper large-v3",
                index_time="14.2s",
                created_at=utc_now() - timedelta(days=2),
                processed_at=utc_now() - timedelta(days=2),
            )
            e2 = Episode(
                id="ep-002",
                project_id=p1.id if p1 else None,
                title="React Server Components Deep Dive",
                description="A deep look into server rendering, streaming hydration, and state patterns in modern React.",
                original_filename="rsc_deep_dive.mp3",
                audio_url="/mock/storage/rsc_deep_dive.mp3",
                file_size=75497472, # ~72 MB
                mime_type="audio/mpeg",
                duration=4325.0, # 1:12:05
                status="completed",
                processing_model="Whisper large-v3",
                index_time="18.5s",
                created_at=utc_now() - timedelta(days=3),
                processed_at=utc_now() - timedelta(days=3),
            )
            e3 = Episode(
                id="ep-003",
                project_id=p2.id if p2 else None,
                title="Machine Learning Ops",
                description="Managing model deployment pipelines, observability, and drift detection.",
                original_filename="ml_ops_pipeline.mp3",
                audio_url="/mock/storage/ml_ops_pipeline.mp3",
                file_size=40108032, # ~38 MB
                mime_type="audio/mpeg",
                duration=2295.0, # 38:15
                status="processing",
                processing_model="Whisper large-v3",
                created_at=utc_now(),
            )
            e4 = Episode(
                id="ep-004",
                project_id=p2.id if p2 else None,
                title="The Future of AI Agents",
                description="Autonomous agents, multi-agent frameworks, tool use, and safety alignment.",
                original_filename="future_of_ai_agents.mp3",
                audio_url="/mock/storage/future_of_ai_agents.mp3",
                file_size=58327040, # ~55 MB
                mime_type="audio/mpeg",
                duration=3340.0, # 55:40
                status="completed",
                processing_model="Whisper large-v3",
                index_time="16.8s",
                created_at=utc_now() - timedelta(days=4),
                processed_at=utc_now() - timedelta(days=4),
            )
            e5 = Episode(
                id="ep-005",
                project_id=p4.id if p4 else None,
                title="Kubernetes Networking Basics",
                description="Understanding CNI plugins, ingress controllers, overlay networks, and service meshes.",
                original_filename="k8s_networking.mp3",
                audio_url="/mock/storage/k8s_networking.mp3",
                file_size=44302336,
                mime_type="audio/mpeg",
                duration=2538.0, # 42:18
                status="completed",
                processing_model="Whisper large-v3",
                index_time="11.4s",
                created_at=utc_now() - timedelta(days=5),
                processed_at=utc_now() - timedelta(days=5),
            )
            e6 = Episode(
                id="ep-006",
                project_id=p1.id if p1 else None,
                title="Building a Vector Database",
                description="HNSW indexing, product quantization, IVF, and SIMD distance computations in Rust.",
                original_filename="building_vector_db.mp3",
                audio_url="/mock/storage/building_vector_db.mp3",
                file_size=68681728,
                mime_type="audio/mpeg",
                duration=3930.0, # 1:05:30
                status="completed",
                processing_model="Whisper large-v3",
                index_time="22.1s",
                created_at=utc_now() - timedelta(days=6),
                processed_at=utc_now() - timedelta(days=6),
            )
            e7 = Episode(
                id="ep-007",
                project_id=None,
                title="Corrupted Audio File",
                description="Sample corrupted file upload demonstrating error recovery.",
                original_filename="corrupted_sample.mp3",
                audio_url="/mock/storage/corrupted_sample.mp3",
                file_size=0,
                mime_type="audio/mpeg",
                duration=0.0,
                status="failed",
                created_at=utc_now() - timedelta(days=7),
            )
            e8 = Episode(
                id="ep-008",
                project_id=p3.id if p3 else None,
                title="Interview with CTO on Architecture",
                description="Lessons learned growing engineering teams from 10 to 500 engineers.",
                original_filename="cto_interview.mp3",
                audio_url="/mock/storage/cto_interview.mp3",
                file_size=50554470,
                mime_type="audio/mpeg",
                duration=2892.0, # 48:12
                status="completed",
                processing_model="Whisper large-v3",
                index_time="15.0s",
                created_at=utc_now() - timedelta(days=8),
                processed_at=utc_now() - timedelta(days=8),
            )
            db.add_all([e1, e2, e3, e4, e5, e6, e7, e8])
            db.commit()

            # 4. Speakers for ep-001
            s1 = Speaker(id="spk-1", episode_id=e1.id, label="Speaker 1", display_name="Alex Morgan", speaking_duration=920.0, segment_count=5)
            s2 = Speaker(id="spk-2", episode_id=e1.id, label="Speaker 2", display_name="Priya Shah", speaking_duration=1140.0, segment_count=6)
            s3 = Speaker(id="spk-3", episode_id=e1.id, label="Speaker 3", display_name="Daniel Chen", speaking_duration=662.0, segment_count=2)
            db.add_all([s1, s2, s3])
            db.commit()

            # 5. Transcript Segments for ep-001 matching the exact frontend player text
            transcript_data = [
                (1, s1.id, 0.0, 18.0, "Welcome back to the Engineering Podcast. Today we're diving deep into a topic that almost every growing engineering organization faces eventually: the transition from a monolithic architecture to microservices, and more specifically, how to manage state and consistency when you do that."),
                (2, s2.id, 18.0, 28.0, "Thanks Alex. It's great to be here. This is definitely one of those architectural challenges that looks straightforward on a whiteboard but gets incredibly messy in production."),
                (3, s1.id, 28.0, 39.0, "Exactly. Before we get into the solutions, let's talk about the pain points. When did you realize at your previous company that the monolith was no longer serving you?"),
                (4, s2.id, 39.0, 62.0, "It wasn't a single moment, but rather a slow degradation of developer velocity. Our database became the integration point for every team. If the billing team needed to add a column, they had to coordinate with the fulfillment team because they were querying the same tables. Deployments took hours, and rollbacks were terrifying."),
                (5, s3.id, 62.0, 76.0, "I'll add to that. The cognitive load for new engineers was immense. You couldn't just understand one domain; you had to understand how your changes might trigger side effects across a 5-million line codebase."),
                (6, s1.id, 76.0, 81.0, "So you decided to split it up. What was the first boundary you drew?"),
                (7, s2.id, 81.0, 102.0, "We started with the lowest risk, highest isolation component: email and notifications. It didn't need synchronous access to core transaction data, so we could wrap it in an event-driven interface. We set up a Kafka cluster and just started publishing domain events from the monolith."),
                (8, s3.id, 102.0, 114.0, "Which sounds great until you realize your event publisher and your database transaction aren't atomic. That's when we hit our first major distributed systems outage."),
                (9, s1.id, 114.0, 125.0, "The classic dual-write problem. Let's dig into that. How did you resolve it?"),
                (10, s2.id, 125.0, 142.0, "We eventually implemented the Transactional Outbox pattern. Instead of publishing to Kafka directly from the application code, we wrote the event to an 'outbox' table within the exact same database transaction that updated our core domain entities."),
                (11, s3.id, 142.0, 165.0, "Right, and then a separate background worker—often called a relay or a CDC process—tails that outbox table and actually pushes the messages to the broker. If the application crashes immediately after committing to the database, the event is still safely stored and will eventually be published."),
                (12, s1.id, 165.0, 173.0, "That guarantees at-least-once delivery. But how did you handle the potential for duplicate events downstream?"),
                (13, s2.id, 173.0, 200.0, "Idempotency. Every consumer of those events had to be designed to be idempotent. We enforced a strict pattern where every event had a unique ID, and consumers had to track which IDs they had already processed. It required a significant shift in how our teams thought about database writes."),
            ]

            segments = []
            for seq, spk_id, start_t, end_t, txt in transcript_data:
                seg = TranscriptSegment(
                    id=f"seg-001-{seq}",
                    episode_id=e1.id,
                    speaker_id=spk_id,
                    start_time=start_t,
                    end_time=end_t,
                    text=txt,
                    sequence_number=seq,
                    confidence=0.98,
                )
                segments.append(seg)
            db.add_all(segments)
            db.commit()

            # 6. Embeddings for segments
            for seg in segments:
                emb = Embedding(
                    id=f"emb-{seg.id}",
                    segment_id=seg.id,
                    embedding=[0.01 * (i % 10) for i in range(1536)],
                )
                db.add(emb)
            db.commit()

            # 7. Episode Insight for ep-001
            insight1 = EpisodeInsight(
                id="ins-001",
                episode_id=e1.id,
                overview="Comprehensive exploration of decomposing monolithic databases and adopting event-driven distributed architectures with transactional outbox and idempotency guarantees.",
                competencies=[
                    "Distributed Systems Architecture",
                    "Transactional Outbox & CDC Patterns",
                    "Eventual Consistency & Idempotent Consumer Design",
                    "Zero-Downtime Database Migration"
                ],
                technologies=["PostgreSQL", "Apache Kafka", "Debezium", "PgBouncer", "Redis", "Docker"],
                architecture=[
                    "Transactional Outbox Relay Pattern",
                    "Event-Driven Microservices Messaging",
                    "Connection Pooling & Connection Starvation Mitigation",
                    "Dead Letter Queues & Exponential Backoff Strategies"
                ],
                resume_bullet="Architected high-throughput event-driven microservices using the Transactional Outbox pattern and Debezium CDC, eliminating dual-write anomalies and maintaining 99.99% data consistency during monolithic database decomposition."
            )
            db.add(insight1)
            db.commit()

        # 8. Seed Processing Jobs
        if db.query(ProcessingJob).count() == 0:
            ep1 = db.query(Episode).filter(Episode.id == "ep-001").first()
            ep2 = db.query(Episode).filter(Episode.id == "ep-002").first()
            ep3 = db.query(Episode).filter(Episode.id == "ep-003").first()
            ep7 = db.query(Episode).filter(Episode.id == "ep-007").first()

            j1 = ProcessingJob(
                id="job-1",
                episode_id=ep3.id if ep3 else "ep-003",
                status="processing",
                current_stage="transcription",
                progress=45,
                started_at=utc_now() - timedelta(minutes=12),
            )
            j2 = ProcessingJob(
                id="job-2",
                episode_id=ep7.id if ep7 else "ep-007",
                status="failed",
                current_stage="speaker_detection",
                progress=32,
                error_message="Audio header corrupted at frame 402.",
                started_at=utc_now() - timedelta(hours=2),
                completed_at=utc_now() - timedelta(hours=1, minutes=55),
            )
            j3 = ProcessingJob(
                id="job-3",
                episode_id=ep1.id if ep1 else "ep-001",
                status="completed",
                current_stage="complete",
                progress=100,
                started_at=utc_now() - timedelta(days=1),
                completed_at=utc_now() - timedelta(days=1) + timedelta(minutes=18),
            )
            j4 = ProcessingJob(
                id="job-4",
                episode_id=ep2.id if ep2 else "ep-002",
                status="completed",
                current_stage="complete",
                progress=100,
                started_at=utc_now() - timedelta(days=1),
                completed_at=utc_now() - timedelta(days=1) + timedelta(minutes=14),
            )
            db.add_all([j1, j2, j3, j4])
            db.commit()

        # 9. Seed Saved Searches
        if db.query(SavedSearch).count() == 0:
            searches = [
                SavedSearch(id="s-1", user_id=user.id, name="Database Bottlenecks", query="Where do they discuss database bottlenecks?", filters=["Engineering Podcasts", "All Speakers"], run_count=24, last_run_at=utc_now() - timedelta(days=1)),
                SavedSearch(id="s-2", user_id=user.id, name="Vector Database Discussions", query="Which episodes compare vector databases?", filters=["Data Science", "Recent (30 days)"], run_count=12, last_run_at=utc_now() - timedelta(days=4)),
                SavedSearch(id="s-3", user_id=user.id, name="Engineering Hiring", query="What do the guests say about hiring senior engineers?", filters=["Leadership"], run_count=45, last_run_at=utc_now() - timedelta(days=9)),
                SavedSearch(id="s-4", user_id=user.id, name="Incident Response", query="Where do they discuss production incidents?", filters=["SRE / DevOps", "All Speakers"], run_count=8, last_run_at=utc_now() - timedelta(days=11)),
                SavedSearch(id="s-5", user_id=user.id, name="Kubernetes Scaling", query="Find discussions about Kubernetes scaling problems.", filters=["Infrastructure", "All Speakers"], run_count=31, last_run_at=utc_now() - timedelta(days=19)),
                SavedSearch(id="s-6", user_id=user.id, name="AI Infrastructure", query="Where do they discuss the cost of running AI infrastructure?", filters=["AI / ML", "Recent (60 days)"], run_count=19, last_run_at=utc_now() - timedelta(days=24)),
                SavedSearch(id="s-7", user_id=user.id, name="Observability", query="How do they approach monitoring distributed systems?", filters=["Engineering Podcasts", "SRE / DevOps"], run_count=56, last_run_at=utc_now() - timedelta(days=32)),
            ]
            db.add_all(searches)
            db.commit()

        # 10. Seed Notifications
        if db.query(Notification).count() == 0:
            notifs = [
                Notification(id="n-1", user_id=user.id, type="processing_complete", title="Episode processing completed", description='"Scaling Distributed Systems" is ready to search.', link="/episodes/ep-001", read=False, created_at=utc_now() - timedelta(minutes=2)),
                Notification(id="n-2", user_id=user.id, type="processing_failed", title="Episode processing failed", description='"Corrupted Audio File" could not be processed.', link="/processing", read=False, created_at=utc_now() - timedelta(minutes=18)),
                Notification(id="n-3", user_id=user.id, type="saved_search", title="New saved search result", description='"Database Bottlenecks" returned 4 new relevant segments.', link="/search", read=False, created_at=utc_now() - timedelta(hours=1)),
                Notification(id="n-4", user_id=user.id, type="transcript_indexed", title="Transcript indexed", description='"Building a Vector Database" has been added to semantic search.', link="/episodes/ep-006", read=True, created_at=utc_now() - timedelta(hours=3)),
                Notification(id="n-5", user_id=user.id, type="processing_started", title="Processing started", description='"Machine Learning Ops" is being transcribed.', link="/processing", read=True, created_at=utc_now() - timedelta(hours=5)),
            ]
            db.add_all(notifs)
            db.commit()

        print("Development seed data populated successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
