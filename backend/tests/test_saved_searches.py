import pytest
from backend.models import User, SavedSearch, Episode, TranscriptSegment, Embedding
from backend.services.embedding_service import MockEmbeddingService

@pytest.fixture
def user_and_episode(db):
    user = User(id="user-saved-test", email="saved-test@example.com")
    ep = Episode(id="ep-saved-1", title="Database Optimization", status="completed")
    seg = TranscriptSegment(
        id="seg-saved-1",
        episode_id=ep.id,
        start_time=10.0,
        end_time=30.0,
        text="Indexing strategies for high-throughput Postgres tables.",
        sequence_number=1,
    )
    embedder = MockEmbeddingService()
    emb = Embedding(id="emb-saved-1", segment_id=seg.id, embedding=embedder.generate_deterministic_vector(seg.text))
    db.add_all([user, ep, seg, emb])
    db.flush()
    return user

def test_saved_searches_crud_flow(client, user_and_episode):
    headers = {"X-User-Id": "user-saved-test"}

    # 1. Create Saved Search
    create_payload = {
        "name": "Database Scaling Queries",
        "description": "Finds all episodes discussing PostgreSQL bottlenecks",
        "query": "Postgres indexing high-throughput",
        "filters": ["Engineering", "All Speakers"],
    }
    res_create = client.post("/api/search/saved", json=create_payload, headers=headers)
    assert res_create.status_code == 200
    created = res_create.json()
    assert created["name"] == "Database Scaling Queries"
    assert created["user_id"] == "user-saved-test"
    search_id = created["id"]

    # 2. Get All Saved Searches
    res_get_all = client.get("/api/search/saved", headers=headers)
    assert res_get_all.status_code == 200
    all_searches = res_get_all.json()
    assert len(all_searches) >= 1
    assert any(s["id"] == search_id for s in all_searches)

    # 3. Get Single Saved Search
    res_get_single = client.get(f"/api/search/saved/{search_id}", headers=headers)
    assert res_get_single.status_code == 200
    assert res_get_single.json()["query"] == "Postgres indexing high-throughput"

    # 4. Update Saved Search
    update_payload = {
        "name": "Database Scaling & Performance Queries",
        "description": "Updated note",
    }
    res_update = client.patch(f"/api/search/saved/{search_id}", json=update_payload, headers=headers)
    assert res_update.status_code == 200
    assert res_update.json()["name"] == "Database Scaling & Performance Queries"

    # 5. Run Saved Search (reuses SemanticSearchService)
    res_run = client.post(f"/api/search/saved/{search_id}/run", headers=headers)
    assert res_run.status_code == 200
    search_results = res_run.json()
    assert search_results["query"] == "Postgres indexing high-throughput"
    assert "results" in search_results
    assert search_results["total_matches"] >= 1

    # Verify run count incremented
    res_after_run = client.get(f"/api/search/saved/{search_id}", headers=headers)
    assert res_after_run.json()["run_count"] == 1
    assert res_after_run.json()["last_run_at"] is not None

    # 6. Delete Saved Search
    res_delete = client.delete(f"/api/search/saved/{search_id}", headers=headers)
    assert res_delete.status_code == 200

    # Verify Deleted
    res_get_deleted = client.get(f"/api/search/saved/{search_id}", headers=headers)
    assert res_get_deleted.status_code == 404
