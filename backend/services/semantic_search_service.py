import time
import math
import re
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from backend.models.embedding import Embedding
from backend.models.transcript_segment import TranscriptSegment
from backend.models.episode import Episode
from backend.models.speaker import Speaker
from backend.models.project import Project
from backend.services.embedding_service import MockEmbeddingService
from backend.services import embedding_service
from backend.schemas.search_schemas import SearchRequest, SearchResponse, SearchResultItem

def format_duration(seconds: float) -> str:
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return max(0.0, min(1.0, dot / (norm1 * norm2)))

def extract_highlighted_context(text: str, query: str) -> Dict[str, str]:
    words = [w.lower() for w in re.findall(r'\w+', query) if len(w) > 3]
    if not words:
        words = query.lower().split()

    text_lower = text.lower()
    best_pos = -1
    for w in words:
        pos = text_lower.find(w)
        if pos != -1:
            best_pos = pos
            break

    if best_pos == -1:
        # Fallback: highlight first clause or middle
        split_idx = min(len(text), 60)
        return {
            "context_before": "",
            "highlight": text[:split_idx],
            "context_after": text[split_idx:]
        }

    start = max(0, best_pos - 40)
    end = min(len(text), best_pos + 60)
    
    # Adjust to word boundaries
    if start > 0:
        space_idx = text.find(" ", start)
        if space_idx != -1 and space_idx < best_pos:
            start = space_idx + 1

    return {
        "context_before": text[:start],
        "highlight": text[start:end],
        "context_after": text[end:]
    }

class SemanticSearchService:
    async def search(
        self,
        db: Session,
        request: SearchRequest,
    ) -> SearchResponse:
        start_time_t = time.perf_counter()

        # 1. Generate query embedding
        query_vector = await embedding_service.embed_text(request.query)

        # 2. Check dialect to determine pgvector execution
        is_postgres = False
        if db.bind and db.bind.dialect.name == "postgresql":
            is_postgres = True

        top_results = []
        if is_postgres:
            # Native PostgreSQL pgvector cosine distance calculation in SQL
            distance_expr = Embedding.embedding.cosine_distance(query_vector)
            similarity_expr = (1.0 - distance_expr).label("similarity")

            q = (
                db.query(Embedding, TranscriptSegment, Episode, similarity_expr)
                .join(TranscriptSegment, Embedding.segment_id == TranscriptSegment.id)
                .join(Episode, TranscriptSegment.episode_id == Episode.id)
                .options(joinedload(TranscriptSegment.speaker))
            )

            # Apply SQL Filters
            if request.project_id and request.project_id != "all":
                q = q.filter(Episode.project_id == request.project_id)

            if request.episode_ids:
                q = q.filter(Episode.id.in_(request.episode_ids))

            if request.speaker_ids and "all" not in request.speaker_ids:
                q = q.filter(TranscriptSegment.speaker_id.in_(request.speaker_ids))

            # Apply similarity threshold in SQL
            if request.similarity_threshold > 0:
                q = q.filter(similarity_expr >= request.similarity_threshold)

            # Order by distance ascending (similarity descending) and limit in SQL
            top_records = q.order_by(distance_expr.asc()).limit(request.limit).all()

            top_results = [
                (float(sim), emb, seg, ep) for emb, seg, ep, sim in top_records
            ]
        else:
            # SQLite fallback for local test environments without pgvector
            q = (
                db.query(Embedding, TranscriptSegment, Episode)
                .join(TranscriptSegment, Embedding.segment_id == TranscriptSegment.id)
                .join(Episode, TranscriptSegment.episode_id == Episode.id)
                .options(joinedload(TranscriptSegment.speaker))
            )

            if request.project_id and request.project_id != "all":
                q = q.filter(Episode.project_id == request.project_id)

            if request.episode_ids:
                q = q.filter(Episode.id.in_(request.episode_ids))

            if request.speaker_ids and "all" not in request.speaker_ids:
                q = q.filter(TranscriptSegment.speaker_id.in_(request.speaker_ids))

            candidates = q.all()
            scored_results = []

            for emb, seg, ep in candidates:
                emb_vec = emb.embedding
                if hasattr(emb_vec, "tolist"):
                    emb_vec = emb_vec.tolist()
                elif isinstance(emb_vec, str):
                    import json
                    emb_vec = json.loads(emb_vec)

                sim = cosine_similarity(query_vector, emb_vec)
                if sim >= request.similarity_threshold:
                    scored_results.append((sim, emb, seg, ep))

            scored_results.sort(key=lambda x: x[0], reverse=True)
            top_results = scored_results[:request.limit]

        # 5. Format results
        result_items: List[SearchResultItem] = []
        for sim, emb, seg, ep in top_results:
            spk = seg.speaker
            spk_name = spk.display_name or spk.label if spk else "Unknown Speaker"
            
            # Derive color
            spk_color = "text-sky-400"
            if "priya" in spk_name.lower():
                spk_color = "text-emerald-400"
            elif "alex" in spk_name.lower():
                spk_color = "text-indigo-400"
            elif "daniel" in spk_name.lower() or "chen" in spk_name.lower():
                spk_color = "text-amber-400"

            ctx = extract_highlighted_context(seg.text, request.query)
            proj_name = ep.project.name if ep.project else "General"

            result_items.append(
                SearchResultItem(
                    id=f"res-{seg.id}",
                    episode_id=ep.id,
                    episode_title=ep.title,
                    project=proj_name,
                    speaker=spk_name,
                    speaker_color=spk_color,
                    start_time=seg.start_time,
                    end_time=seg.end_time,
                    timestamp=format_duration(seg.start_time),
                    time_sec=seg.start_time,
                    text=seg.text,
                    highlight=ctx["highlight"],
                    context_before=ctx["context_before"],
                    context_after=ctx["context_after"],
                    score=round(sim, 4),
                    match_score=int(round(sim * 100)),
                )
            )

        elapsed_ms = round((time.perf_counter() - start_time_t) * 1000, 2)

        return SearchResponse(
            query=request.query,
            total_matches=len(result_items),
            execution_time_ms=elapsed_ms,
            results=result_items,
        )

semantic_search_service = SemanticSearchService()
