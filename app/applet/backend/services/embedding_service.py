class EmbeddingService:
    def generate_embedding(self, text: str):
        pass

class MockEmbeddingService(EmbeddingService):
    def generate_embedding(self, text: str):
        # Mock 1536-dimensional vector for pgvector testing
        return [0.0] * 1536
