from datetime import datetime
from backend.schemas.episode_schemas import (
    EpisodeBase, EpisodeCreate, EpisodeResponse,
    SpeakerBase, SpeakerResponse,
    TranscriptSegmentBase, TranscriptSegmentResponse,
    EpisodeInsightBase, EpisodeInsightResponse
)
from backend.schemas.search_schemas import SearchRequest, SavedSearchCreate

def test_episode_schema_validation():
    create_data = EpisodeCreate(title="Test Episode", description="Description")
    assert create_data.title == "Test Episode"
    assert create_data.language == "en"

def test_speaker_schema_validation():
    spk = SpeakerBase(label="Speaker 1", display_name="Alex", speaking_duration=120.5)
    assert spk.label == "Speaker 1"
    assert spk.speaking_duration == 120.5

def test_search_request_bounds():
    req = SearchRequest(query="distributed state", similarity_threshold=0.8, limit=5)
    assert req.query == "distributed state"
    assert req.similarity_threshold == 0.8
    assert req.limit == 5

def test_insight_schema():
    insight = EpisodeInsightBase(
        overview="Overview summary",
        competencies=["Design", "Architecture"],
        technologies=["PostgreSQL", "FastAPI"],
        architecture=["Clean Architecture"],
        resume_bullet="Built backend foundation with FastAPI and PostgreSQL."
    )
    assert len(insight.competencies) == 2
    assert "FastAPI" in insight.technologies
