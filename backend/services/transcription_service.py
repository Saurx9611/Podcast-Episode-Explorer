import asyncio
from typing import List, Dict, Any
from backend.services.base import BaseTranscriptionService

class MockTranscriptionService(BaseTranscriptionService):
    """
    Isolated development transcription service.
    Generates realistic timestamped conversational transcript segments.
    """
    async def transcribe(self, audio_path: str, title: str = "") -> List[Dict[str, Any]]:
        # Simulate realistic async processing delay
        await asyncio.sleep(0.5)

        base_topic = title or "System Engineering & Cloud Architecture"
        return [
            {
                "text": f"Welcome everyone to today's deep dive into {base_topic}. Today we're exploring production lessons and architectural tradeoffs.",
                "start_time": 0.0,
                "end_time": 18.5,
                "confidence": 0.98,
            },
            {
                "text": "When we initially designed our core ingestion engine, we noticed severe bottlenecks during high-throughput peaks.",
                "start_time": 18.5,
                "end_time": 42.0,
                "confidence": 0.96,
            },
            {
                "text": "Right, and the primary reason was synchronous database write locks on our primary transactional instance.",
                "start_time": 42.0,
                "end_time": 68.2,
                "confidence": 0.97,
            },
            {
                "text": "To solve that, we decomposed the monolith into event-driven workers using an asynchronous queue with backpressure control.",
                "start_time": 68.2,
                "end_time": 95.8,
                "confidence": 0.95,
            },
            {
                "text": "How did you guarantee idempotency and avoid duplicate message processing across distributed consumer pods?",
                "start_time": 95.8,
                "end_time": 120.4,
                "confidence": 0.99,
            },
            {
                "text": "We utilized distributed deduplication keys stored in Redis with atomic lease expirations alongside transactional outbox patterns.",
                "start_time": 120.4,
                "end_time": 154.0,
                "confidence": 0.94,
            },
            {
                "text": "That reduced our P99 latency by over 65% and allowed linear autoscaling without database saturation.",
                "start_time": 154.0,
                "end_time": 180.5,
                "confidence": 0.98,
            }
        ]

def get_transcription_service(provider: str = None) -> BaseTranscriptionService:
    """Factory to retrieve the appropriate transcription service provider."""
    from backend.core.config import settings
    selected_provider = (provider or settings.TRANSCRIPTION_PROVIDER or "mock").lower()

    if selected_provider in ("faster_whisper", "whisper", "real"):
        from backend.services.whisper_transcription_service import FasterWhisperTranscriptionService
        return FasterWhisperTranscriptionService()
    
    return MockTranscriptionService()
