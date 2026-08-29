class ChunkingService:
    def chunk(self, text: str):
        pass

class MockChunkingService(ChunkingService):
    def chunk(self, text: str):
        return [text]
