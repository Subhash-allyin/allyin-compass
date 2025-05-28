from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List


class EmbeddingEngine:
    """Centralized embedding functionality for the entire system"""
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingEngine, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._model is None:
            try:
                self._model = SentenceTransformer('all-MiniLM-L6-v2')
                print(" Embedding engine initialized")
            except Exception as e:
                print(f" Embedding engine failed: {e}")
                self._model = None
    
    @property
    def available(self) -> bool:
        """Check if embedding model is available"""
        return self._model is not None
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for text list"""
        if not self._model:
            return np.array([])
        
        try:
            embeddings = self._model.encode(texts)
            return embeddings
        except Exception as e:
            print(f"Embedding error: {e}")
            return np.array([])
    
    def encode_single(self, text: str) -> np.ndarray:
        """Create embedding for single text"""
        if not self._model:
            return np.array([])
        return self.encode([text])[0]
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        if not self._model:
            return 0.0
        
        try:
            embeddings = self.encode([text1, text2])
            if len(embeddings) == 2:
                # Cosine similarity
                similarity = np.dot(embeddings[0], embeddings[1]) / (
                    np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
                )
                return float(similarity)
        except:
            pass
        
        return 0.0

# Singleton instance
embedding_engine = EmbeddingEngine()
