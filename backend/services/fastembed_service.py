import asyncio
import logging
from typing import List, Optional
from backend.services.base import BaseEmbeddingService
from backend.core.config import settings
from backend.core.exceptions import ValidationException

logger = logging.getLogger("backend.services.fastembed")

MODEL_DIMENSIONS = {
    "BAAI/bge-small-en-v1.5": 384,
    "BAAI/bge-base-en-v1.5": 768,
    "BAAI/bge-large-en-v1.5": 1024,
    "sentence-transformers/all-MiniLM-L6-v2": 384,
    "nomic-ai/nomic-embed-text-v1.5": 768,
    "text-embedding-3-small": 1536,
}

class FastEmbedEmbeddingService(BaseEmbeddingService):
    """
    Production embedding service using fastembed (ONNX-runtime accelerated).
    Generates fast, high-quality, normalized dense embeddings locally.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.DEFAULT_EMBEDDING_MODEL
        self._model = None

    @property
    def dimension(self) -> int:
        return MODEL_DIMENSIONS.get(self.model_name, 384)

    def _get_model(self):
        """Lazy-loads FastEmbed TextEmbedding model on first inference call."""
        if self._model is None:
            try:
                from fastembed import TextEmbedding
            except ImportError:
                raise ValidationException(
                    "fastembed is not installed. Please install fastembed or set EMBEDDING_PROVIDER=mock."
                )

            logger.info(f"Loading FastEmbed model '{self.model_name}'...")
            self._model = TextEmbedding(model_name=self.model_name)
            logger.info(f"FastEmbed model '{self.model_name}' loaded successfully (dim={self.dimension}).")
        return self._model

    def _embed_sync(self, texts: List[str]) -> List[List[float]]:
        model = self._get_model()
        cleaned_texts = [t.strip() if t and t.strip() else "content" for t in texts]
        embeddings_gen = model.embed(cleaned_texts)
        results = []
        for emb in embeddings_gen:
            # Convert numpy array to standard Python list of floats
            results.append([round(float(x), 6) for x in emb])
        return results

    async def embed_text(self, text: str) -> List[float]:
        if not text or not text.strip():
            text = "empty"
        batch_results = await self.embed_batch([text])
        return batch_results[0]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        # Run CPU-bound ONNX inference in worker thread
        return await asyncio.to_thread(self._embed_sync, texts)
