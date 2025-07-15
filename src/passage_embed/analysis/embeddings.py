"""Embedding generation module for passage embedding analysis."""

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Any, Tuple
from halo import Halo

from ..core.exceptions import EmbeddingError
from ..core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingGenerator:
    """Generator for text embeddings using sentence transformers."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize embedding generator.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            with Halo(text=f"Loading SentenceTransformer model: {self.model_name}", spinner="dots") as spinner:
                self.model = SentenceTransformer(self.model_name)
                spinner.succeed(f"Model {self.model_name} loaded successfully")
        except Exception as e:
            raise EmbeddingError(f"Failed to load model {self.model_name}: {e}")
    
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
                    embedding = self.model.encode(element["value"])
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
                query_embeddings = self.model.encode(queries)
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


def generate_embeddings(texts: List[str], model_name: str = 'all-MiniLM-L6-v2') -> np.ndarray:
    """Convenience function to generate embeddings.
    
    Args:
        texts: List of text strings to embed
        model_name: Name of the sentence transformer model
        
    Returns:
        Array of embeddings
    """
    generator = EmbeddingGenerator(model_name)
    return generator.generate_embeddings(texts) 