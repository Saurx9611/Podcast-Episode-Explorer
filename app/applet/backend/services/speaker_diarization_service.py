class SpeakerDiarizationService:
    def diarize(self, audio_path: str):
        pass

class MockSpeakerDiarizationService(SpeakerDiarizationService):
    def diarize(self, audio_path: str):
        return [
            {"speaker": "Speaker 1", "start": 0.0, "end": 5.0},
            {"speaker": "Speaker 2", "start": 5.0, "end": 10.0}
        ]
