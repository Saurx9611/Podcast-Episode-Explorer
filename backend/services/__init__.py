from .base import (
    BaseTranscriptionService,
    BaseSpeakerDiarizationService,
    BaseChunkingService,
    BaseEmbeddingService,
    BaseInsightService,
)
from .transcription_service import MockTranscriptionService
from .speaker_diarization_service import MockSpeakerDiarizationService
from .chunking_service import SpeakerAwareChunkingService
from .embedding_service import MockEmbeddingService
from .insight_service import EpisodeInsightService, MockInsightService

# Singleton dev / mock instances
transcription_service: BaseTranscriptionService = MockTranscriptionService()
speaker_diarization_service: BaseSpeakerDiarizationService = MockSpeakerDiarizationService()
chunking_service: BaseChunkingService = SpeakerAwareChunkingService()
embedding_service: BaseEmbeddingService = MockEmbeddingService()
insight_service: BaseInsightService = EpisodeInsightService()

__all__ = [
    "BaseTranscriptionService",
    "BaseSpeakerDiarizationService",
    "BaseChunkingService",
    "BaseEmbeddingService",
    "BaseInsightService",
    "MockTranscriptionService",
    "MockSpeakerDiarizationService",
    "SpeakerAwareChunkingService",
    "MockEmbeddingService",
    "MockInsightService",
    "EpisodeInsightService",
    "transcription_service",
    "speaker_diarization_service",
    "chunking_service",
    "embedding_service",
    "insight_service",
]
