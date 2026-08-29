import pytest
from backend.models import User, Episode, Speaker, TranscriptSegment, Embedding, Project
from backend.services.embedding_service import MockEmbeddingService

@pytest.fixture
def search_fixtures(db):
    user = User(id="user-search-1", email="search-user@example.com", name="Search Tester")
    proj1 = Project(id="proj-s-1", user_id=user.id, name="Distributed Systems Hub")
    proj2 = Project(id="proj-s-2", user_id=user.id, name="Frontend Engineering")

    ep1 = Episode(id="ep-s-1", project_id=proj1.id, title="Distributed Consensus & Caching", duration=300.0, status="completed")
    ep2 = Episode(id="ep-s-2", project_id=proj2.id, title="React Server Components Architecture", duration=400.0, status="completed")

    spk1 = Speaker(id="spk-s-1", episode_id=ep1.id, label="Speaker 1", display_name="Dr. Leslie Lamport")
    spk2 = Speaker(id="spk-s-2", episode_id=ep1.id, label="Speaker 2", display_name="Martin Kleppmann")
    spk3 = Speaker(id="spk-s-3", episode_id=ep2.id, label="Speaker 1", display_name="Dan Abramov")

    seg1 = TranscriptSegment(
        id="seg-s-1",
        episode_id=ep1.id,
        speaker_id=spk1.id,
        start_time=45.5,
        end_time=80.0,
        text="Paxos and Raft handle state machine replication in distributed consensus.",
        sequence_number=1,
    )
    seg2 = TranscriptSegment(
        id="seg-s-2",
        episode_id=ep1.id,
        speaker_id=spk2.id,
        start_time=80.0,
        end_time=120.0,
        text="Transactional outbox and dual writes solve database consistency with Kafka brokers.",
        sequence_number=2,
    )
    seg3 = TranscriptSegment(
        id="seg-s-3",
        episode_id=ep2.id,
        speaker_id=spk3.id,
        start_time=10.0,
        end_time=50.0,
        text="Streaming SSR and Suspense boundaries reduce client bundle hydration costs.",
        sequence_number=1,
    )

    embedder = MockEmbeddingService()
    emb1 = Embedding(id="emb-s-1", segment_id=seg1.id, embedding=embedder.generate_deterministic_vector(seg1.text))
    emb2 = Embedding(id="emb-s-2", segment_id=seg2.id, embedding=embedder.generate_deterministic_vector(seg2.text))
    emb3 = Embedding(id="emb-s-3", segment_id=seg3.id, embedding=embedder.generate_deterministic_vector(seg3.text))

    db.add_all([user, proj1, proj2, ep1, ep2, spk1, spk2, spk3, seg1, seg2, seg3, emb1, emb2, emb3])
    db.flush()

    return {"ep1": ep1, "ep2": ep2, "spk1": spk1, "spk2": spk2, "spk3": spk3}

def test_semantic_search_ranking(client, search_fixtures):
    payload = {
        "query": "distributed consensus state machine replication",
        "similarity_threshold": 0.0,
        "limit": 5,
    }
    res = client.post("/api/search", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_matches"] > 0
    results = data["results"]
    assert len(results) >= 2
    # Verify top result is highest score
    assert results[0]["score"] >= results[1]["score"]
    assert "consensus" in results[0]["text"].lower() or "replication" in results[0]["text"].lower()

def test_semantic_search_episode_filtering(client, search_fixtures):
    payload = {
        "query": "database",
        "episode_ids": ["ep-s-1"],
        "similarity_threshold": 0.0,
        "limit": 10,
    }
    res = client.post("/api/search", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert all(r["episode_id"] == "ep-s-1" for r in data["results"])

def test_semantic_search_speaker_filtering(client, search_fixtures):
    payload = {
        "query": "architecture",
        "speaker_ids": ["spk-s-3"],
        "similarity_threshold": 0.0,
        "limit": 10,
    }
    res = client.post("/api/search", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["speaker"] == "Dan Abramov"

def test_semantic_search_similarity_threshold(client, search_fixtures):
    payload = {
        "query": "completely unrelated cooking recipe with tomatoes and cheese",
        "similarity_threshold": 0.99,
        "limit": 10,
    }
    res = client.post("/api/search", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["results"]) == 0

def test_timestamp_navigation_fields(client, search_fixtures):
    payload = {
        "query": "Transactional outbox",
        "similarity_threshold": 0.0,
        "limit": 1,
    }
    res = client.post("/api/search", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert len(data["results"]) > 0
    top = data["results"][0]
    assert top["start_time"] == 80.0
    assert top["time_sec"] == 80.0
    assert top["timestamp"] in ["01:20", "1:20"]
