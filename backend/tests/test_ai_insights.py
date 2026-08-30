import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

from backend.main import app
from backend.core.database import SessionLocal, init_db
from backend.models.episode import Episode
from backend.models.episode_insight import EpisodeInsight
from backend.repositories.episode_repo import EpisodeRepository
from backend.services.llm_insight_service import (
    RuleBasedInsightService,
    GeminiInsightService,
    OpenAIInsightService,
    get_insight_service,
    build_aggregated_context,
    validate_and_sanitize_insights,
)

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

def test_insight_provider_factory():
    mock_svc = get_insight_service("mock")
    assert isinstance(mock_svc, RuleBasedInsightService)

    gemini_svc = get_insight_service("gemini")
    assert isinstance(gemini_svc, GeminiInsightService)

    openai_svc = get_insight_service("openai")
    assert isinstance(openai_svc, OpenAIInsightService)

    auto_svc = get_insight_service("auto")
    assert isinstance(auto_svc, (RuleBasedInsightService, GeminiInsightService, OpenAIInsightService))

def test_build_aggregated_context_windowing():
    title = "Scaling Postgres Beyond 100TB"
    
    # 1. Short transcript
    short_transcript = "Short podcast transcript about relational database indexing."
    short_ctx = build_aggregated_context(title, short_transcript, max_chars=1000)
    assert short_transcript in short_ctx
    assert title in short_ctx

    # 2. Long transcript (> 50,000 characters)
    long_transcript = "Paragraph talking about sharding and partitioning. " * 1500
    assert len(long_transcript) > 70000

    aggregated_ctx = build_aggregated_context(title, long_transcript, max_chars=8000)
    assert len(aggregated_ctx) <= 12000
    assert "--- INTRODUCTION ---" in aggregated_ctx
    assert "--- KEY DISCUSSION SEGMENTS ---" in aggregated_ctx
    assert "--- CONCLUSION & SUMMARY ---" in aggregated_ctx
    assert "[... discussion continues ...]" in aggregated_ctx

def test_validate_and_sanitize_insights():
    # 1. Complete valid input
    valid_input = {
        "overview": "Clear architectural summary of microservices.",
        "competencies": ["Distributed Systems", "Caching", "Async Queues"],
        "technologies": ["PostgreSQL", "Redis", "Kafka"],
        "architecture": ["Step 1", "Step 2", "Step 3"],
        "resume_bullet": "Led engineering migration from monolith to event-driven microservices.",
    }
    sanitized = validate_and_sanitize_insights(valid_input, "Episode 1")
    assert sanitized["overview"] == valid_input["overview"]
    assert len(sanitized["competencies"]) == 3
    assert len(sanitized["technologies"]) == 3
    assert sanitized["resume_bullet"] == valid_input["resume_bullet"]

    # 2. Incomplete/malformed input (None/empty fields)
    malformed_input = {
        "overview": None,
        "competencies": [],
        "technologies": None,
        "architecture": "not a list",
        "resume_bullet": "",
    }
    sanitized_bad = validate_and_sanitize_insights(malformed_input, "Episode 2")
    assert isinstance(sanitized_bad["overview"], str)
    assert len(sanitized_bad["overview"]) > 10
    assert isinstance(sanitized_bad["competencies"], list)
    assert len(sanitized_bad["competencies"]) >= 3
    assert isinstance(sanitized_bad["technologies"], list)
    assert len(sanitized_bad["technologies"]) >= 3
    assert isinstance(sanitized_bad["architecture"], list)
    assert len(sanitized_bad["architecture"]) >= 3
    assert isinstance(sanitized_bad["resume_bullet"], str)
    assert len(sanitized_bad["resume_bullet"]) > 10

@pytest.mark.anyio
async def test_rule_based_insight_service():
    svc = RuleBasedInsightService()
    transcript = "We discussed PostgreSQL optimization, pgvector cosine search, Kafka event streaming, and FastAPI microservices."
    insights = await svc.generate_insights("Event-Driven Search Infrastructure", transcript)

    assert "overview" in insights
    assert "competencies" in insights
    assert "technologies" in insights
    assert "architecture" in insights
    assert "resume_bullet" in insights
    assert any("PostgreSQL" in t for t in insights["technologies"])
    assert any("pgvector" in t for t in insights["technologies"])

@pytest.mark.anyio
async def test_gemini_service_mocked_success():
    svc = GeminiInsightService(api_key="mock-api-key")

    mock_gemini_response = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": '{"overview": "LLM synthesized overview of distributed databases.", "competencies": ["Distributed Consensus", "Partitioning"], "technologies": ["PostgreSQL", "Raft", "Redis"], "architecture": ["Step 1", "Step 2"], "resume_bullet": "Built distributed raft consensus store."}'
                        }
                    ]
                }
            }
        ]
    }

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_gemini_response
        mock_post.return_value = mock_resp

        insights = await svc.generate_insights("Raft Consensus Podcast", "Discussing Raft consensus in distributed databases.")
        assert insights["overview"] == "LLM synthesized overview of distributed databases."
        assert "Distributed Consensus" in insights["competencies"]
        assert "Raft" in insights["technologies"]

@pytest.mark.anyio
async def test_gemini_service_fallback_on_error():
    svc = GeminiInsightService(api_key="mock-api-key")

    with patch("httpx.AsyncClient.post", side_effect=Exception("API connection timeout")):
        # Should gracefully fall back to RuleBasedInsightService without crashing
        insights = await svc.generate_insights("Resilient Systems", "Discussing fault tolerance and database replication.")
        assert "overview" in insights
        assert isinstance(insights["technologies"], list)
        assert len(insights["technologies"]) >= 3

def test_api_insights_endpoints(db_session):
    ep_repo = EpisodeRepository(db_session)
    ep = Episode(
        title="Scaling Microservices with Kafka",
        status="completed"
    )
    created_ep = ep_repo.create(ep)

    try:
        # 1. GET /api/episodes/{id}/insights (generates on demand and persists)
        res = client.get(f"/api/episodes/{created_ep.id}/insights")
        assert res.status_code == 200
        data = res.json()
        assert "overview" in data
        assert "competencies" in data
        assert "technologies" in data
        assert "architecture" in data
        assert "resume_bullet" in data
        assert data["episode_id"] == created_ep.id

        # 2. Check persistence in database
        persisted = ep_repo.get_insights(created_ep.id)
        assert persisted is not None
        assert persisted.overview == data["overview"]

        # 3. POST /api/episodes/{id}/insights/generate (explicit re-generation)
        regen_res = client.post(f"/api/episodes/{created_ep.id}/insights/generate")
        assert regen_res.status_code == 200
        regen_data = regen_res.json()
        assert regen_data["episode_id"] == created_ep.id

    finally:
        ep_repo.delete(created_ep.id)
