import pytest
from backend.models import User, Project, Episode, TranscriptSegment, EpisodeInsight
from backend.services.insight_service import MockInsightService

@pytest.fixture
def episode_with_transcript(db):
    user = User(id="user-insight-test", email="insight-test@example.com")
    ep = Episode(
        id="ep-insight-1",
        title="Scaling Distributed Systems Without Sacrificing Reliability",
        description="A masterclass on distributed systems, Kafka queues, and PostgreSQL indexing.",
        status="completed"
    )
    seg1 = TranscriptSegment(
        id="seg-ins-1",
        episode_id=ep.id,
        start_time=0.0,
        end_time=20.0,
        text="We faced severe connection exhaustion on our primary PostgreSQL writer.",
        sequence_number=1,
    )
    seg2 = TranscriptSegment(
        id="seg-ins-2",
        episode_id=ep.id,
        start_time=20.0,
        end_time=50.0,
        text="Introducing Redis distributed locks and an asynchronous Kafka outbox resolved the bottlenecks.",
        sequence_number=2,
    )
    db.add_all([user, ep, seg1, seg2])
    db.flush()
    return ep

def test_insight_service_generation():
    service = MockInsightService()
    import asyncio
    res = asyncio.run(service.generate_insights(
        "Scaling Distributed Systems Without Sacrificing Reliability",
        "We faced severe connection exhaustion on our primary PostgreSQL writer."
    ))
    assert "overview" in res
    assert isinstance(res["competencies"], list)
    assert len(res["competencies"]) >= 3
    assert isinstance(res["technologies"], list)
    assert len(res["technologies"]) >= 3
    assert isinstance(res["architecture"], list)
    assert len(res["architecture"]) >= 2
    assert "resume_bullet" in res
    assert len(res["resume_bullet"]) > 20

def test_get_episode_insights_api(client, episode_with_transcript):
    headers = {"X-User-Id": "user-insight-test"}
    res = client.get(f"/api/episodes/{episode_with_transcript.id}/insights", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["episode_id"] == episode_with_transcript.id
    assert "overview" in data
    assert "competencies" in data and len(data["competencies"]) > 0
    assert "technologies" in data and len(data["technologies"]) > 0
    assert "architecture" in data and len(data["architecture"]) > 0
    assert "resume_bullet" in data

def test_get_episode_insights_not_found(client):
    headers = {"X-User-Id": "default-user"}
    res = client.get("/api/episodes/non-existent-ep/insights", headers=headers)
    assert res.status_code == 404
