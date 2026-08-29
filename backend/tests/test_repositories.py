from backend.models import User, Project, Episode, Speaker, TranscriptSegment, SavedSearch, Notification, ProcessingJob
from backend.repositories import (
    UserRepository, ProjectRepository, EpisodeRepository,
    SearchRepository, ProcessingRepository, NotificationRepository
)
from backend.schemas.search_schemas import SavedSearchCreate, SavedSearchUpdate

def test_user_repository(db):
    repo = UserRepository(db)
    user = repo.get_or_create_default_user()
    assert user is not None
    assert user.id == "dev-user-id"

def test_project_repository(db):
    user_repo = UserRepository(db)
    user = user_repo.get_or_create_default_user()
    
    proj_repo = ProjectRepository(db)
    proj = Project(id="p-repo-test", user_id=user.id, name="Test Project", description="Description")
    proj_repo.create(proj)

    stats = proj_repo.get_project_with_stats("p-repo-test")
    assert stats is not None
    assert stats["name"] == "Test Project"
    assert stats["episodes_count"] == 0

def test_episode_repository(db):
    ep_repo = EpisodeRepository(db)
    episode = Episode(
        id="ep-repo-1",
        title="Scaling Microservices",
        duration=1200.0,
        status="completed"
    )
    ep_repo.create(episode)
    
    speaker = Speaker(id="spk-repo-1", episode_id="ep-repo-1", label="Speaker 1", display_name="Dev")
    db.add(speaker)
    
    segment = TranscriptSegment(
        id="seg-repo-1",
        episode_id="ep-repo-1",
        speaker_id="spk-repo-1",
        start_time=0.0,
        end_time=10.0,
        text="Intro segment",
        sequence_number=1
    )
    db.add(segment)
    db.commit()

    assert len(ep_repo.get_episodes()) >= 1
    assert len(ep_repo.get_transcript("ep-repo-1")) == 1
    assert len(ep_repo.get_speakers("ep-repo-1")) == 1

def test_search_and_notifications_repositories(db):
    user_repo = UserRepository(db)
    user = user_repo.get_or_create_default_user()
    
    search_repo = SearchRepository(db)
    created = search_repo.create_saved_search(
        user.id,
        SavedSearchCreate(name="DB query", query="database", filters=["SQL"])
    )
    assert created.id is not None
    
    # Record run
    updated_search = search_repo.record_search_run(created.id)
    assert updated_search.run_count == 1
    assert updated_search.last_run_at is not None

    notif_repo = NotificationRepository(db)
    notif = Notification(user_id=user.id, type="system", title="Welcome", read=False)
    notif_repo.create(notif)
    assert notif_repo.get_unread_count(user.id) >= 1

    notif_repo.mark_all_as_read(user.id)
    assert notif_repo.get_unread_count(user.id) == 0
