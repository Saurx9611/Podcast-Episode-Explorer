import asyncio
from typing import List, Dict, Any, Tuple
from backend.services.base import BaseSpeakerDiarizationService

class MockSpeakerDiarizationService(BaseSpeakerDiarizationService):
    """
    Isolated development speaker diarization service.
    Assigns speaker labels and computes speaking durations.
    """
    async def diarize(
        self, audio_path: str, raw_segments: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        await asyncio.sleep(0.4)

        speakers_def = [
            {"label": "Speaker 1", "display_name": "Alex Morgan"},
            {"label": "Speaker 2", "display_name": "Priya Shah"},
        ]

        diarized_segments = []
        speaker_stats: Dict[str, Dict[str, Any]] = {
            "Speaker 1": {"label": "Speaker 1", "display_name": "Alex Morgan", "duration": 0.0, "count": 0},
            "Speaker 2": {"label": "Speaker 2", "display_name": "Priya Shah", "duration": 0.0, "count": 0},
        }

        for idx, seg in enumerate(raw_segments):
            # Alternate speakers realistically
            spk_label = "Speaker 1" if idx % 2 == 0 else "Speaker 2"
            duration = seg["end_time"] - seg["start_time"]

            speaker_stats[spk_label]["duration"] += duration
            speaker_stats[spk_label]["count"] += 1

            diarized_segments.append({
                **seg,
                "speaker_label": spk_label,
                "sequence_number": idx + 1,
            })

        speaker_profiles = list(speaker_stats.values())
        return diarized_segments, speaker_profiles
