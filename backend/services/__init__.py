from .base import (
    BaseTranscriptionService,
    BaseSpeakerDiarizationService,
    BaseChunkingService,
    BaseEmbeddingService,
    BaseInsightService,
)
from .transcription_service import MockTranscriptionService, get_transcription_service
from .whisper_transcription_service import FasterWhisperTranscriptionService
from .speaker_diarization_service import MockSpeakerDiarizationService, get_speaker_diarization_service
from .pyannote_diarization_service import (
    PyannoteSpeakerDiarizationService,
    AcousticSpeakerDiarizationService,
    align_transcript_with_speakers,
)
from .chunking_service import SpeakerAwareChunkingService
from .embedding_service import MockEmbeddingService, get_embedding_service
from .fastembed_service import FastEmbedEmbeddingService
from .insight_service import (
    EpisodeInsightService,
    MockInsightService,
    RuleBasedInsightService,
    GeminiInsightService,
    OpenAIInsightService,
    get_insight_service,
)
from .feed_parser_service import FeedParserService, feed_parser_service
from .podcast_ingestion_service import PodcastIngestionService, podcast_ingestion_service
from .audio_downloader_service import AudioDownloaderService, audio_downloader_service

# Singleton instances initialized according to settings
transcription_service: BaseTranscriptionService = get_transcription_service()
speaker_diarization_service: BaseSpeakerDiarizationService = get_speaker_diarization_service()
chunking_service: BaseChunkingService = SpeakerAwareChunkingService()
embedding_service: BaseEmbeddingService = get_embedding_service()
insight_service: BaseInsightService = get_insight_service()

__all__ = [
    "BaseTranscriptionService",
    "BaseSpeakerDiarizationService",
    "BaseChunkingService",
    "BaseEmbeddingService",
    "BaseInsightService",
    "MockTranscriptionService",
    "FasterWhisperTranscriptionService",
    "get_transcription_service",
    "MockSpeakerDiarizationService",
    "PyannoteSpeakerDiarizationService",
    "AcousticSpeakerDiarizationService",
    "get_speaker_diarization_service",
    "align_transcript_with_speakers",
    "SpeakerAwareChunkingService",
    "MockEmbeddingService",
    "FastEmbedEmbeddingService",
    "get_embedding_service",
    "MockInsightService",
    "EpisodeInsightService",
    "RuleBasedInsightService",
    "GeminiInsightService",
    "OpenAIInsightService",
    "get_insight_service",
    "FeedParserService",
    "feed_parser_service",
    "PodcastIngestionService",
    "podcast_ingestion_service",
    "AudioDownloaderService",
    "audio_downloader_service",
    "transcription_service",
    "speaker_diarization_service",
    "chunking_service",
    "embedding_service",
    "insight_service",
]
