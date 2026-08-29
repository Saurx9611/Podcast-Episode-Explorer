import math
import hashlib
import re
import asyncio
from typing import List
from backend.services.base import BaseEmbeddingService

class MockEmbeddingService(BaseEmbeddingService):
    """
    Mock embedding service producing 1536-dimensional normalized vectors
    using token-level hashing and n-gram projections for realistic semantic similarity.
    """
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension

    def _generate_vector(self, text: str) -> List[float]:
        vec = [0.0] * self.dimension
        words = re.findall(r'\w+', text.lower())
        if not words:
            # Baseline unit vector
            vec[0] = 1.0
            return vec

        # Add single word features and bigram features
        tokens = list(words)
        for i in range(len(words) - 1):
            tokens.append(f"{words[i]}_{words[i+1]}")

        for token in tokens:
            h = hashlib.md5(token.encode('utf-8')).hexdigest()
            # Map token to 3 deterministic indices for density
            idx1 = int(h[0:8], 16) % self.dimension
            idx2 = int(h[8:16], 16) % self.dimension
            idx3 = int(h[16:24], 16) % self.dimension

            sign1 = 1.0 if int(h[24], 16) % 2 == 0 else -1.0
            sign2 = 1.0 if int(h[25], 16) % 2 == 0 else -1.0
            sign3 = 1.0 if int(h[26], 16) % 2 == 0 else -1.0

            vec[idx1] += 1.0 * sign1
            vec[idx2] += 0.5 * sign2
            vec[idx3] += 0.25 * sign3

        # L2 Normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [round(x / norm, 6) for x in vec]
        else:
            vec[0] = 1.0

        return vec

    def generate_deterministic_vector(self, text: str) -> List[float]:
        return self._generate_vector(text)

    async def embed_text(self, text: str) -> List[float]:
        await asyncio.sleep(0.01)
        return self._generate_vector(text)

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        await asyncio.sleep(0.02)
        return [self._generate_vector(t) for t in texts]
