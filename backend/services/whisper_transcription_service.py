import os
import math
import asyncio
import logging
from typing import List, Dict, Any, Optional

from backend.services.base import BaseTranscriptionService
from backend.core.config import settings
from backend.core.exceptions import ValidationException

logger = logging.getLogger("backend.services.whisper_transcription")

class FasterWhisperTranscriptionService(BaseTranscriptionService):
    """
    Production transcription service using faster-whisper (CTranslate2).
    Provides fast, local, GPU/CPU-accelerated speech-to-text with timestamped segments.
    """

    def __init__(
        self,
        model_size: Optional[str] = None,
        device: Optional[str] = None,
        compute_type: Optional[str] = None,
    ):
        self.model_size = model_size or settings.WHISPER_MODEL_SIZE
        self.device = device or settings.WHISPER_DEVICE
        self.compute_type = compute_type or settings.WHISPER_COMPUTE_TYPE
        self._model = None

    def _get_model(self):
        """Lazy-loads the faster-whisper model on first transcription call."""
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError:
                raise ValidationException(
                    "faster-whisper is not installed. Please install faster-whisper or set TRANSCRIPTION_PROVIDER=mock."
                )

            logger.info(
                f"Loading faster-whisper model '{self.model_size}' on device '{self.device}' with compute_type '{self.compute_type}'..."
            )
            # Default auto device resolution
            selected_device = self.device
            if selected_device == "auto":
                selected_device = "cpu"

            selected_compute = self.compute_type
            if selected_compute == "default":
                selected_compute = "int8" if selected_device == "cpu" else "float16"

            self._model = WhisperModel(
                self.model_size,
                device=selected_device,
                compute_type=selected_compute,
            )
            logger.info("faster-whisper model initialized successfully.")
        return self._model

    def _transcribe_sync(self, audio_path: str) -> List[Dict[str, Any]]:
        """Synchronous transcription worker executed in thread pool."""
        model = self._get_model()
        segments_generator, info = model.transcribe(
            audio_path,
            beam_size=5,
            word_timestamps=False,
            vad_filter=True,
        )

        results: List[Dict[str, Any]] = []
        for segment in segments_generator:
            text = segment.text.strip()
            if not text:
                continue

            # Calculate confidence score from avg_logprob: e^(avg_logprob)
            confidence = 0.95
            if hasattr(segment, "avg_logprob") and segment.avg_logprob is not None:
                try:
                    raw_conf = math.exp(segment.avg_logprob)
                    confidence = round(max(0.0, min(1.0, float(raw_conf))), 3)
                except (OverflowError, ValueError):
                    confidence = 0.95

            results.append({
                "text": text,
                "start_time": round(float(segment.start), 2),
                "end_time": round(float(segment.end), 2),
                "confidence": confidence,
            })

        return results

    async def transcribe(self, audio_path: str, title: str = "") -> List[Dict[str, Any]]:
        """Transcribes the audio file asynchronously, returning timestamped segments."""
        if not audio_path:
            raise ValidationException("Audio file path is missing.")

        if not os.path.exists(audio_path):
            raise ValidationException(f"Audio file '{audio_path}' does not exist on disk.")

        if os.path.getsize(audio_path) == 0:
            raise ValidationException(f"Audio file '{audio_path}' is empty (0 bytes).")

        logger.info(f"Starting faster-whisper transcription for: {audio_path}")

        try:
            # Run CPU/GPU bound inference in worker threadpool to avoid blocking async event loop
            segments = await asyncio.to_thread(self._transcribe_sync, audio_path)
            
            if not segments:
                raise ValidationException("No speech or transcription segments detected in audio file.")

            logger.info(f"Transcription complete: extracted {len(segments)} segments for '{title or audio_path}'")
            return segments
        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}", exc_info=True)
            raise ValidationException(f"Whisper transcription error: {str(e)}")
