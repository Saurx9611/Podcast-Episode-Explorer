import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient

from backend.main import app
from backend.core.database import SessionLocal, init_db
from backend.models.episode import Episode
from backend.models.speaker import Speaker
from backend.models.transcript_segment import TranscriptSegment
from backend.models.embedding import Embedding
from backend.repositories.episode_repo import EpisodeRepository
from backend.repositories.search_repo import SearchRepository
from backend.services.embedding_service import MockEmbeddingService, get_embedding_service
from backend.services.fastembed_service import FastEmbedEmbeddingService
from backend.services.semantic_search_service import SemanticSearchService
from backend.schemas.search_schemas import SearchRequest, SavedSearchCreate

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_embedding_provider_factory():
    mock_svc = get_embedding_service("mock")
    assert isinstance(mock_svc, MockEmbeddingService)

    fastembed_svc = get_embedding_service("fastembed")
    assert isinstance(fastembed_svc, FastEmbedEmbeddingService)
    assert fastembed_svc.dimension == 384

@pytest.mark.anyio
async def test_fastembed_service_generation():
    svc = FastEmbedEmbeddingService(model_name="BAAI/bge-small-en-v1.5")
    assert svc.dimension == 384

    # 1. Single text
    vec = await svc.embed_text("Distributed consensus and vector database indexing")
    assert isinstance(vec, list)
    assert len(vec) == 384
    # Check non-zero
    assert any(x != 0.0 for x in vec)

    # 2. Batch
    batch = await svc.embed_batch(["First sentence", "Second sentence"])
    assert len(batch) == 2
    assert len(batch[0]) == 384
    assert len(batch[1]) == 384

@pytest.mark.anyio
async def test_semantic_search_filtering_and_threshold(db_session):
    ep_repo = EpisodeRepository(db_session)
    search_service = SemanticSearchService()

    # 1. Create episode
    ep = Episode(
        title="Vector Search & AI Infrastructure",
        status="completed",
    )
    created_ep = ep_repo.create(ep)

    # 2. Create speaker
    speaker = Speaker(
        episode_id=created_ep.id,
        label="Speaker 1",
        display_name="Alex Chen",
        speaking_duration=120.0,
        segment_count=2,
    )
    db_session.add(speaker)
    db_session.flush()

    # 3. Create transcript segment with embedding
    mock_emb = MockEmbeddingService()
    seg_text = "PostgreSQL pgvector provides high dimensional vector similarity indexing using HNSW."
    vec = await mock_emb.embed_text(seg_text)

    segment = TranscriptSegment(
        episode_id=created_ep.id,
        speaker_id=speaker.id,
        start_time=12.5,
        end_time=35.0,
        text=seg_text,
        sequence_number=1,
        confidence=0.98,
    )
    db_session.add(segment)
    db_session.flush()

    emb_record = Embedding(
        segment_id=segment.id,
        embedding=vec,
    )
    db_session.add(emb_record)
    db_session.commit()

    try:
        # 4. Search matching query
        req = SearchRequest(
            query="pgvector similarity indexing",
            similarity_threshold=0.3,
            limit=10,
        )
        res = await search_service.search(db_session, req)
        assert res.total_matches >= 1
        top_match = res.results[0]
        assert top_match.episode_id == created_ep.id
        assert top_match.speaker == "Alex Chen"
        assert top_match.start_time == 12.5
        assert top_match.end_time == 35.0
        assert top_match.score >= 0.3

        # 5. Search with speaker filter
        req_speaker = SearchRequest(
            query="pgvector",
            speaker_ids=[speaker.id],
            similarity_threshold=0.1,
        )
        res_spk = await search_service.search(db_session, req_speaker)
        assert res_spk.total_matches >= 1

        # 6. Search with non-matching speaker filter
        req_other_speaker = SearchRequest(
            query="pgvector",
            speaker_ids=["non-existent-speaker-id"],
            similarity_threshold=0.1,
        )
        res_other = await search_service.search(db_session, req_other_speaker)
        assert res_other.total_matches == 0

        # 7. Search with unattainable threshold
        req_high_thresh = SearchRequest(
            query="pgvector",
            similarity_threshold=0.99999,
        )
        res_none = await search_service.search(db_session, req_high_thresh)
        assert res_none.total_matches == 0

    finally:
        ep_repo.delete(created_ep.id)

def test_api_search_and_saved_search(db_session):
    # 1. Test POST /api/search
    search_resp = client.post("/api/search", json={
        "query": "system architecture and databases",
        "similarity_threshold": 0.0,
        "limit": 5,
    })
    assert search_resp.status_code == 200
    data = search_resp.json()
    assert "results" in data
    assert "total_matches" in data
    assert "execution_time_ms" in data

    # 2. Test Saved Search CRUD and Execution
    create_saved = client.post("/api/search/saved", json={
        "name": "Database Scaling Queries",
        "query": "database scaling",
        "description": "Monitors database discussions",
        "filters": ["database", "scale"],
    })
    assert create_saved.status_code in (200, 201)
    saved_id = create_saved.json()["id"]

    # Run saved search
    run_resp = client.post(f"/api/search/saved/{saved_id}/run")
    assert run_resp.status_code == 200
    run_data = run_resp.json()
    assert "results" in run_data
    assert run_data["query"] == "database scaling"

    # Cleanup
    client.delete(f"/api/search/saved/{saved_id}")
