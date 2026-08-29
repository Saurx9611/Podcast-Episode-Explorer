from backend.models import (
    User, Project, Episode, Speaker, TranscriptSegment,
    Embedding, ProcessingJob, SavedSearch, Notification, EpisodeInsight
)

def test_create_and_query_user(db):
    user = User(
        id="test-user-1",
        email="test@example.com",
        name="Test User",
        role="Engineer",
        preferences={"theme": "dark"}
    )
    db.add(user)
    db.commit()

    queried = db.query(User).filter(User.id == "test-user-1").first()
    assert queried is not None
    assert queried.email == "test@example.com"
    assert queried.preferences["theme"] == "dark"

def test_create_episode_hierarchy(db):
    user = User(id="user-hier", email="hier@example.com")
    project = Project(id="proj-hier", user_id=user.id, name="Test Project")
    episode = Episode(
        id="ep-hier",
        project_id=project.id,
        title="Distributed Caching Patterns",
        duration=1800.0,
        status="completed"
    )
    speaker = Speaker(
        id="spk-hier",
        episode_id=episode.id,
        label="Speaker 1",
        display_name="Sarah Connor"
    )
    segment = TranscriptSegment(
        id="seg-hier",
        episode_id=episode.id,
        speaker_id=speaker.id,
        start_time=10.0,
        end_time=25.5,
        text="Let us discuss cache invalidation.",
        sequence_number=1
    )
    insight = EpisodeInsight(
        id="ins-hier",
        episode_id=episode.id,
        overview="Cache invalidation deep dive.",
        competencies=["Caching", "Redis"],
        technologies=["Redis", "Memcached"],
        architecture=["Cache-Aside Pattern"],
        resume_bullet="Improved API latency by 80% implementing Cache-Aside with Redis."
    )
    
    db.add_all([user, project, episode, speaker, segment, insight])
    db.commit()

    # Query back and verify relations
    fetched_ep = db.query(Episode).filter(Episode.id == "ep-hier").first()
    assert fetched_ep is not None
    assert len(fetched_ep.speakers) == 1
    assert fetched_ep.speakers[0].display_name == "Sarah Connor"
    assert len(fetched_ep.transcript_segments) == 1
    assert fetched_ep.transcript_segments[0].start_time == 10.0
    assert fetched_ep.insight is not None
    assert "Redis" in fetched_ep.insight.technologies

def test_create_saved_search_and_notifications(db):
    user = User(id="user-sn", email="sn@example.com")
    saved_search = SavedSearch(
        id="ss-test",
        user_id=user.id,
        name="Cache discussions",
        query="caching algorithms",
        filters=["Engineering", "Redis"]
    )
    notif = Notification(
        id="notif-test",
        user_id=user.id,
        type="processing_complete",
        title="Processing Finished",
        description="Episode ready",
        read=False
    )
    job = ProcessingJob(
        id="job-test",
        episode_id="some-ep-id",
        status="completed",
        progress=100
    )
    db.add_all([user, saved_search, notif, job])
    db.commit()

    assert db.query(SavedSearch).filter(SavedSearch.id == "ss-test").first().name == "Cache discussions"
    assert db.query(Notification).filter(Notification.id == "notif-test").first().read is False
    assert db.query(ProcessingJob).filter(ProcessingJob.id == "job-test").first().progress == 100
