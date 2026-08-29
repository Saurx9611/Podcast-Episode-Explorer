class TranscriptionService:
    def transcribe(self, audio_path: str):
        pass

class MockTranscriptionService(TranscriptionService):
    def transcribe(self, audio_path: str):
        # Mock implementation returning dummy transcript
        return [
            {"start": 0.0, "end": 5.0, "text": "Welcome to the podcast."},
            {"start": 5.0, "end": 10.0, "text": "Today we are discussing databases."}
        ]
