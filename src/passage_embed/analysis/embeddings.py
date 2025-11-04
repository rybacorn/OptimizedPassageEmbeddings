"""Embedding generation module for passage embedding analysis."""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Any, Tuple, Optional
from halo import Halo

from ..core.exceptions import EmbeddingError
from ..core.logging import get_logger

logger = get_logger(__name__)


ALLOWED_MRL_DIMS = {128, 256, 512, 768}


class EmbeddingGenerator:
    """Generator for text embeddings using sentence transformers."""

    def __init__(
        self,
        model_name: str = 'google/embeddinggemma-300m',
        embedding_dim: int = 768,
    ):
        """Initialize embedding generator.

        Args:
            model_name: Name of the sentence transformer model to use.
            embedding_dim: Target embedding dimension when supported (Matryoshka truncation).
        """
        self.model_name = model_name
        self.embedding_dim = embedding_dim
        self.model: Optional[SentenceTransformer] = None
        self.is_gemma = 'embeddinggemma' in self.model_name.lower()
        self._validate_embedding_dim()
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            with Halo(text=f"Loading SentenceTransformer model: {self.model_name}", spinner="dots") as spinner:
                if self.is_gemma:
                    try:
                        import torch
                    except ImportError as import_error:
                        raise EmbeddingError(
                            "PyTorch is required to load EmbeddingGemma models. Please install torch>=2.0.0."
                        ) from import_error

                    target_dtype = torch.bfloat16 if hasattr(torch, 'bfloat16') else torch.float32
                    self.model = SentenceTransformer(
                        self.model_name,
                        model_kwargs={'torch_dtype': target_dtype},
                    )
                else:
                    self.model = SentenceTransformer(self.model_name)
                spinner.succeed(f"Model {self.model_name} loaded successfully")
        except Exception as e:
            raise EmbeddingError(f"Failed to load model {self.model_name}: {e}")

    def _validate_embedding_dim(self) -> None:
        """Validate embedding dimension constraints."""
        if self.embedding_dim is None:
            return

        if not isinstance(self.embedding_dim, int) or self.embedding_dim <= 0:
            raise EmbeddingError("embedding_dim must be a positive integer")

        if self.is_gemma and self.embedding_dim not in ALLOWED_MRL_DIMS:
            raise EmbeddingError(
                f"EmbeddingGemma supports embedding dimensions {sorted(ALLOWED_MRL_DIMS)}, received {self.embedding_dim}."
            )
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            Array of embeddings
        """
        if self.model is None:
            raise EmbeddingError("Model not loaded")
        
        try:
            with Halo(text=f"Generating embeddings for {len(texts)} texts", spinner="dots") as spinner:
                embeddings = self.model.encode(texts)
                embeddings = self._apply_truncation(embeddings)
                spinner.succeed(f"Generated embeddings for {len(texts)} texts")
            return embeddings
        except Exception as e:
            raise EmbeddingError(f"Failed to generate embeddings: {e}")
    
    def process_json_data(self, json_data: Dict[str, List[Dict[str, Any]]], 
                         symbol_mapping: Dict[str, str],
                         size_mapping: Dict[str, int]) -> Tuple[List[Dict[str, Any]], Dict[str, np.ndarray]]:
        """Process JSON data and generate embeddings.
        
        Args:
            json_data: Dictionary mapping sources to content items
            symbol_mapping: Mapping of sources to plot symbols
            size_mapping: Mapping of sources to plot sizes
            
        Returns:
            Tuple of (embeddings_data, mean_embeddings)
        """
        embeddings_data = []
        top_level_embeddings = {}
        
        if self.model is None:
            raise EmbeddingError("Model not loaded")
            
        for url_key, elements in json_data.items():
            element_embeddings = []
            
            for element in elements:
                try:
                    embedding = self._encode_document(element["value"])
                    embedding = self._apply_truncation(embedding)
                    embeddings_data.append({
                        'embedding': embedding,
                        'label': url_key,
                        'type': element["type"],
                        'value': element["value"],
                        'symbol': symbol_mapping.get(element["source"], "circle"),
                        'size': size_mapping.get(element["source"], 8)
                    })
                    element_embeddings.append(embedding)
                except Exception as e:
                    logger.warning(f"Failed to embed element: {element['value'][:50]}... Error: {e}")
                    continue
            
            # Compute mean embedding for each top-level key
            if element_embeddings:
                top_level_embeddings[url_key] = np.mean(element_embeddings, axis=0)
        
        logger.info(f"Processed {len(embeddings_data)} embeddings from {len(json_data)} sources")
        return embeddings_data, top_level_embeddings
    
    def generate_query_embeddings(self, queries: List[str]) -> Tuple[List[Dict[str, Any]], np.ndarray]:
        """Generate embeddings for query list.
        
        Args:
            queries: List of query strings
            
        Returns:
            Tuple of (query_embeddings_data, queries_mean)
        """
        if self.model is None:
            raise EmbeddingError("Model not loaded")
            
        try:
            with Halo(text=f"Generating embeddings for {len(queries)} queries", spinner="dots") as spinner:
                query_embeddings = self._encode_queries(queries)
                query_embeddings = self._apply_truncation(query_embeddings)
                spinner.succeed(f"Generated query embeddings")
            
            query_embeddings_data = [
                {
                    'embedding': embedding,
                    'label': 'Queries',
                    'type': 'Query',
                    'value': queries[i],
                    'symbol': "x",
                    'size': 6
                } for i, embedding in enumerate(query_embeddings)
            ]
            
            queries_mean = np.mean(query_embeddings, axis=0)
            
            logger.info(f"Generated embeddings for {len(queries)} queries")
            return query_embeddings_data, queries_mean
            
        except Exception as e:
            raise EmbeddingError(f"Failed to generate query embeddings: {e}")

    def _encode_document(self, text: str) -> np.ndarray:
        """Encode a document using the appropriate model method."""
        if self.model is None:
            raise EmbeddingError("Model not loaded")

        if self.is_gemma and hasattr(self.model, 'encode_document'):
            embeddings = self.model.encode_document([text])
        else:
            embeddings = self.model.encode([text])

        array = np.asarray(embeddings)
        if array.ndim == 1:
            return array
        return array[0]

    def _encode_queries(self, queries: List[str]) -> np.ndarray:
        """Encode queries using the appropriate model method."""
        if self.model is None:
            raise EmbeddingError("Model not loaded")

        if self.is_gemma and hasattr(self.model, 'encode_query'):
            return np.asarray(self.model.encode_query(queries))

        return np.asarray(self.model.encode(queries))

    def _apply_truncation(self, embeddings: np.ndarray) -> np.ndarray:
        """Apply Matryoshka truncation when requested."""
        if self.embedding_dim is None:
            return embeddings

        array = np.asarray(embeddings)

        if array.ndim == 1:
            return self._truncate_embedding(array)

        if array.ndim == 2:
            return np.array([self._truncate_embedding(vec) for vec in array])

        return array

    def _truncate_embedding(self, embedding: np.ndarray) -> np.ndarray:
        """Truncate an embedding vector and renormalize it."""
        vector = np.asarray(embedding)

        if self.embedding_dim is None or vector.shape[-1] <= self.embedding_dim:
            return vector

        truncated = vector[:self.embedding_dim]
        norm = np.linalg.norm(truncated)
        if norm > 0:
            truncated = truncated / norm
        return truncated


def generate_embeddings(
    texts: List[str],
    model_name: str = 'google/embeddinggemma-300m',
    embedding_dim: int = 768,
) -> np.ndarray:
    """Convenience function to generate embeddings.
    
    Args:
        texts: List of text strings to embed
        model_name: Name of the sentence transformer model
        embedding_dim: Target embedding dimension when supported
        
    Returns:
        Array of embeddings
    """
    generator = EmbeddingGenerator(model_name, embedding_dim)
    return generator.generate_embeddings(texts)