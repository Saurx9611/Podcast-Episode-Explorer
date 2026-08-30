import json
import logging
import re
from typing import Dict, Any, List, Optional
import httpx

from backend.services.base import BaseInsightService
from backend.core.config import settings
from backend.core.exceptions import ValidationException

logger = logging.getLogger("backend.services.insight")

INSIGHT_SYSTEM_PROMPT = """
You are an expert Principal Solutions Architect & Technical Recruiter evaluating an engineering podcast episode.
Synthesize actionable, high-density technical intelligence from the provided podcast transcript.

Return ONLY a valid JSON object matching the following structure:
{
  "overview": "A concise 2-3 sentence executive synthesis of the architectural discussion and engineering trade-offs.",
  "competencies": [
    "Target Competency 1 (e.g. Distributed Consensus & Raft)",
    "Target Competency 2 (e.g. High-Throughput Stream Processing)",
    "Target Competency 3 (e.g. Database Partitioning & Lock Elimination)"
  ],
  "technologies": [
    "Tech 1 (e.g. PostgreSQL)",
    "Tech 2 (e.g. Redis)",
    "Tech 3 (e.g. Apache Kafka)",
    "Tech 4 (e.g. pgvector)"
  ],
  "architecture": [
    "Architectural step 1 (Ingestion & Decoupled Queue Layer)",
    "Architectural step 2 (Temporal Speaker Boundary Detection)",
    "Architectural step 3 (Vector Similarity Search with HNSW)",
    "Architectural step 4 (Distributed Session & Cache Invalidation)"
  ],
  "resume_bullet": "An impactful, metric-driven resume bullet highlighting leadership in designing/scaling the systems discussed."
}
"""

def build_aggregated_context(title: str, full_transcript: str, max_chars: int = 15000) -> str:
    """
    Intelligently samples and aggregates podcast transcript context without exceeding LLM context windows.
    Takes the beginning introduction, evenly spaced discussion highlights, and ending conclusion.
    """
    if not full_transcript or not full_transcript.strip():
        return f"Episode Title: {title}\n(No transcript available)"

    cleaned = full_transcript.strip()
    if len(cleaned) <= max_chars:
        return f"Episode Title: {title}\n\nTranscript:\n{cleaned}"

    # Sample beginning (20%), middle slices (60%), end (20%)
    intro_budget = int(max_chars * 0.25)
    conclusion_budget = int(max_chars * 0.25)
    body_budget = max_chars - (intro_budget + conclusion_budget)

    intro = cleaned[:intro_budget]
    conclusion = cleaned[-conclusion_budget:]
    middle_pool = cleaned[intro_budget:-conclusion_budget]

    # Sample 4 segments from middle pool
    segment_size = len(middle_pool) // 4
    sampled_middle_parts = []
    chunk_take = body_budget // 4
    for i in range(4):
        start = i * segment_size
        sampled_middle_parts.append(middle_pool[start : start + chunk_take])

    aggregated_middle = "\n\n[... discussion continues ...]\n\n".join(sampled_middle_parts)

    return (
        f"Episode Title: {title}\n\n"
        f"--- INTRODUCTION ---\n{intro}\n\n"
        f"--- KEY DISCUSSION SEGMENTS ---\n{aggregated_middle}\n\n"
        f"--- CONCLUSION & SUMMARY ---\n{conclusion}"
    )

def validate_and_sanitize_insights(data: Dict[str, Any], fallback_title: str) -> Dict[str, Any]:
    """
    Validates and guarantees that the insight payload has all 4 required sections with appropriate types.
    """
    overview = data.get("overview")
    if not overview or not isinstance(overview, str) or len(overview.strip()) < 10:
        overview = f"Technical architectural synthesis for {fallback_title}. Analyzes system scalability, distributed patterns, and production engineering trade-offs."

    competencies = data.get("competencies")
    if not isinstance(competencies, list) or len(competencies) == 0:
        competencies = [
            "Distributed Systems Architecture",
            "High-Throughput Ingestion Pipelines",
            "Vector Indexing & Semantic Search",
            "Database Optimization & Partitioning"
        ]
    else:
        competencies = [str(c).strip() for c in competencies if str(c).strip()][:6]

    technologies = data.get("technologies")
    if not isinstance(technologies, list) or len(technologies) == 0:
        technologies = ["PostgreSQL", "FastAPI", "Redis", "pgvector", "Docker"]
    else:
        technologies = [str(t).strip() for t in technologies if str(t).strip()][:8]

    architecture = data.get("architecture")
    if not isinstance(architecture, list) or len(architecture) == 0:
        architecture = [
            "Asynchronous ingestion pipeline with decoupled worker queues and backpressure safeguards",
            "Speaker-aware temporal windowing with precision timestamp preservation",
            "Vector embeddings generation indexed via PostgreSQL pgvector cosine similarity",
            "Distributed caching and session lease controls reducing writer node saturation"
        ]
    else:
        architecture = [str(a).strip() for a in architecture if str(a).strip()][:6]

    resume_bullet = data.get("resume_bullet")
    if not resume_bullet or not isinstance(resume_bullet, str) or len(resume_bullet.strip()) < 10:
        top_tech = technologies[0] if technologies else "distributed databases"
        resume_bullet = f"Architected and deployed an event-driven intelligence pipeline for {fallback_title.lower()}, leveraging {top_tech} to achieve sub-50ms query latency across high-volume workloads."

    return {
        "overview": overview.strip(),
        "competencies": competencies,
        "technologies": technologies,
        "architecture": architecture,
        "resume_bullet": resume_bullet.strip(),
    }


class RuleBasedInsightService(BaseInsightService):
    """
    Deterministic rule-based keyword & pattern insight generator.
    Provides fast, zero-token generation for local development and testing.
    """

    async def generate_insights(self, episode_title: str, full_transcript: str) -> Dict[str, Any]:
        combined = f"{episode_title} {full_transcript}".lower()

        tech_map = [
            ("PostgreSQL", ["postgres", "postgresql", "sql", "table", "index"]),
            ("pgvector", ["pgvector", "vector", "embedding", "cosine", "hnsw"]),
            ("Redis", ["redis", "cache", "caching", "in-memory", "pubsub"]),
            ("Apache Kafka", ["kafka", "stream", "queue", "partition", "events"]),
            ("Docker & Kubernetes", ["docker", "container", "k8s", "kubernetes", "cluster"]),
            ("FastAPI & Python", ["fastapi", "python", "asyncio", "pydantic", "sqlalchemy"]),
            ("Whisper AI", ["whisper", "speech", "transcription", "diarization"]),
            ("React & Next.js", ["react", "next.js", "frontend", "components", "hooks"]),
        ]

        detected_techs = [name for name, kws in tech_map if any(k in combined for k in kws)]
        if len(detected_techs) < 3:
            for dt in ["PostgreSQL", "FastAPI", "Redis", "pgvector", "Docker"]:
                if dt not in detected_techs:
                    detected_techs.append(dt)

        comp_map = [
            ("Distributed Systems Architecture", ["distributed", "scale", "microservices", "latency"]),
            ("High-Throughput Ingestion Pipelines", ["throughput", "ingestion", "pipeline", "batch"]),
            ("Vector Indexing & Similarity Ranking", ["vector", "embedding", "semantic", "ranking"]),
            ("Speaker Diarization & Temporal Chunking", ["speaker", "diarization", "chunking", "transcript"]),
            ("Database Optimization & Isolation", ["database", "query", "index", "locks", "optimization"]),
        ]
        detected_comps = [name for name, kws in comp_map if any(k in combined for k in kws)]
        if len(detected_comps) < 3:
            for dc in ["Distributed Systems Architecture", "High-Throughput Ingestion Pipelines", "Vector Indexing & Similarity Ranking"]:
                if dc not in detected_comps:
                    detected_comps.append(dc)

        return validate_and_sanitize_insights({
            "overview": (
                f"Technical architecture synthesis for '{episode_title}'. "
                f"Examines core system trade-offs focusing on {', '.join(detected_techs[:3])}, "
                f"high-throughput data processing, and production resilience under load."
            ),
            "competencies": detected_comps,
            "technologies": detected_techs,
            "architecture": [
                "Asynchronous ingestion pipeline with decoupled worker queues and backpressure safeguards",
                "Speaker-aware temporal windowing with precision boundary timestamp preservation",
                "Vector embeddings generation indexed via PostgreSQL pgvector cosine similarity",
                "Distributed caching and session lease controls reducing writer node saturation"
            ],
            "resume_bullet": (
                f"Designed and deployed an event-driven ingestion & semantic indexing engine for {episode_title.lower()}, "
                f"leveraging {detected_techs[0]} to achieve sub-50ms query latency while scaling across 100K+ audio segments."
            )
        }, episode_title)


class GeminiInsightService(BaseInsightService):
    """
    LLM-powered InsightService utilizing the Google Gemini API (Gemini 2.5 Flash).
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.DEFAULT_INSIGHT_MODEL or "gemini-2.5-flash"
        self._fallback = RuleBasedInsightService()

    async def generate_insights(self, episode_title: str, full_transcript: str) -> Dict[str, Any]:
        if not self.api_key:
            logger.info("No GEMINI_API_KEY configured. Falling back to RuleBasedInsightService.")
            return await self._fallback.generate_insights(episode_title, full_transcript)

        context = build_aggregated_context(episode_title, full_transcript)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{INSIGHT_SYSTEM_PROMPT}\n\nPodcast Context:\n{context}"}
                    ]
                }
            ],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2,
            }
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code != 200:
                    logger.warning(f"Gemini API returned status {resp.status_code}: {resp.text}. Falling back.")
                    return await self._fallback.generate_insights(episode_title, full_transcript)

                data = resp.json()
                text_out = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(text_out)
                return validate_and_sanitize_insights(parsed, episode_title)
        except Exception as e:
            logger.warning(f"Gemini Insight generation failed: {e}. Falling back to RuleBasedInsightService.")
            return await self._fallback.generate_insights(episode_title, full_transcript)


class OpenAIInsightService(BaseInsightService):
    """
    LLM-powered InsightService utilizing OpenAI Chat Completions (GPT-4o-mini).
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model
        self._fallback = RuleBasedInsightService()

    async def generate_insights(self, episode_title: str, full_transcript: str) -> Dict[str, Any]:
        if not self.api_key:
            logger.info("No OPENAI_API_KEY configured. Falling back to RuleBasedInsightService.")
            return await self._fallback.generate_insights(episode_title, full_transcript)

        context = build_aggregated_context(episode_title, full_transcript)
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": INSIGHT_SYSTEM_PROMPT},
                {"role": "user", "content": context}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code != 200:
                    logger.warning(f"OpenAI API returned {resp.status_code}: {resp.text}. Falling back.")
                    return await self._fallback.generate_insights(episode_title, full_transcript)

                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                return validate_and_sanitize_insights(parsed, episode_title)
        except Exception as e:
            logger.warning(f"OpenAI Insight generation failed: {e}. Falling back.")
            return await self._fallback.generate_insights(episode_title, full_transcript)


def get_insight_service(provider: Optional[str] = None) -> BaseInsightService:
    """Factory to retrieve the appropriate InsightService implementation."""
    selected_provider = (provider or settings.INSIGHT_PROVIDER or "auto").lower()

    if selected_provider == "gemini":
        return GeminiInsightService()
    elif selected_provider == "openai":
        return OpenAIInsightService()
    elif selected_provider == "mock" or selected_provider == "rule":
        return RuleBasedInsightService()
    elif selected_provider == "auto":
        if settings.GEMINI_API_KEY:
            return GeminiInsightService()
        elif settings.OPENAI_API_KEY:
            return OpenAIInsightService()
        return RuleBasedInsightService()

    return RuleBasedInsightService()
