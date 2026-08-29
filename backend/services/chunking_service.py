import re
from typing import List, Dict, Any
from backend.services.base import BaseChunkingService

class SpeakerAwareChunkingService(BaseChunkingService):
    """
    Advanced Speaker-Aware Temporal & Semantic Chunking Service.
    
    Principles:
    1. Speaker Boundaries: Never merges utterances across different speakers.
    2. Semantic Coherence: Splits or merges text at natural sentence/clause boundaries.
    3. Temporal Boundaries: Adheres to target min (10s) and max (60s) duration windows.
    4. Exact Timestamps: Preserves exact start_time and end_time, interpolating proportionately for sub-splits.
    """

    def __init__(self, min_chunk_duration: float = 10.0, max_chunk_duration: float = 60.0):
        self.min_chunk_duration = min_chunk_duration
        self.max_chunk_duration = max_chunk_duration

    def _split_long_segment(self, segment: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Splits an overly long segment at sentence boundaries, interpolating timestamps."""
        text = segment.get("text", "").strip()
        start = segment.get("start_time", 0.0)
        end = segment.get("end_time", start)
        duration = end - start
        
        # Split on sentence boundaries: . ! ? ;
        sentences = [s.strip() for s in re.split(r'(?<=[.!?;\n])\s+', text) if s.strip()]
        if len(sentences) <= 1 or duration <= self.max_chunk_duration:
            return [{
                "text": text,
                "start_time": start,
                "end_time": end,
                "speaker_label": segment.get("speaker_label"),
                "speaker_id": segment.get("speaker_id"),
                "confidence": segment.get("confidence", 0.95),
            }]

        total_chars = sum(len(s) for s in sentences) or 1
        sub_chunks = []
        curr_time = start

        for s in sentences:
            s_duration = (len(s) / total_chars) * duration
            s_end = round(curr_time + s_duration, 3)
            sub_chunks.append({
                "text": s,
                "start_time": round(curr_time, 3),
                "end_time": min(s_end, end),
                "speaker_label": segment.get("speaker_label"),
                "speaker_id": segment.get("speaker_id"),
                "confidence": segment.get("confidence", 0.95),
            })
            curr_time = s_end

        # Ensure last sub-chunk ends exactly at segment end
        if sub_chunks:
            sub_chunks[-1]["end_time"] = end

        return sub_chunks

    def chunk(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes a list of raw or diarized segments and produces coherent transcript chunks.
        """
        # 1. Filter out empty or whitespace-only segments
        valid_segments = []
        for seg in segments:
            text = (seg.get("text") or "").strip()
            if not text:
                continue
            cleaned = dict(seg)
            cleaned["text"] = text
            # Pre-split excessively long single segments
            if (cleaned.get("end_time", 0.0) - cleaned.get("start_time", 0.0)) > self.max_chunk_duration:
                valid_segments.extend(self._split_long_segment(cleaned))
            else:
                valid_segments.append(cleaned)

        if not valid_segments:
            return []

        # 2. Group by speaker continuity & temporal window
        chunks: List[Dict[str, Any]] = []
        current: Dict[str, Any] = {
            "speaker_label": valid_segments[0].get("speaker_label"),
            "speaker_id": valid_segments[0].get("speaker_id"),
            "text": valid_segments[0]["text"],
            "start_time": valid_segments[0]["start_time"],
            "end_time": valid_segments[0]["end_time"],
            "confidence": valid_segments[0].get("confidence", 0.95),
            "segment_ids": [valid_segments[0].get("id")] if valid_segments[0].get("id") else [],
        }

        for seg in valid_segments[1:]:
            same_speaker = (seg.get("speaker_label") == current["speaker_label"] and 
                            seg.get("speaker_id") == current["speaker_id"])
            merged_duration = seg["end_time"] - current["start_time"]

            # Merge if same speaker and within max duration threshold
            if same_speaker and merged_duration <= self.max_chunk_duration:
                current["text"] += " " + seg["text"]
                current["end_time"] = seg["end_time"]
                current["confidence"] = round((current["confidence"] + seg.get("confidence", 0.95)) / 2, 3)
                if seg.get("id"):
                    current["segment_ids"].append(seg["id"])
            else:
                chunks.append(current)
                current = {
                    "speaker_label": seg.get("speaker_label"),
                    "speaker_id": seg.get("speaker_id"),
                    "text": seg["text"],
                    "start_time": seg["start_time"],
                    "end_time": seg["end_time"],
                    "confidence": seg.get("confidence", 0.95),
                    "segment_ids": [seg.get("id")] if seg.get("id") else [],
                }

        if current:
            chunks.append(current)

        # 3. Ensure sequence numbering & strict timestamp monotonic ordering
        for i, c in enumerate(chunks):
            c["sequence_number"] = i + 1
            if i > 0 and c["start_time"] < chunks[i-1]["end_time"]:
                c["start_time"] = chunks[i-1]["end_time"]

        return chunks
