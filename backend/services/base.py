from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple

class BaseTranscriptionService(ABC):
    @abstractmethod
    async def transcribe(self, audio_path: str, title: str = "") -> List[Dict[str, Any]]:
        """
        Transcribes audio into raw timestamped segments.
        Returns:
            List of dicts with:
                text: str
                start_time: float
                end_time: float
                confidence: float
        """
        pass

class BaseSpeakerDiarizationService(ABC):
    @abstractmethod
    async def diarize(
        self, audio_path: str, raw_segments: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Attributes speakers to transcript segments.
        Returns:
            (diarized_segments, speaker_profiles)
        """
        pass

class BaseChunkingService(ABC):
    @abstractmethod
    def chunk(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Performs speaker-aware temporal chunking.
        """
        pass

class BaseEmbeddingService(ABC):
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generates embedding vector for a single string."""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generates embedding vectors for a batch of strings."""
        pass

class BaseInsightService(ABC):
    @abstractmethod
    async def generate_insights(self, episode_title: str, full_transcript: str) -> Dict[str, Any]:
        """
        Generates episode intelligence:
        overview, competencies, technologies, architecture, resume_bullet
        """
        pass
