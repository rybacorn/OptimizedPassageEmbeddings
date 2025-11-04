"""Tests for CLI functionality."""

import sys
from pathlib import Path
import numpy as np
import pytest
from unittest.mock import Mock, patch

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from passage_embed.analysis.embeddings import EmbeddingGenerator


def test_domain_relabeling_in_process_json_data():
    """Test that domain relabeling works correctly with role names."""
    # This tests the logic that's in cli.py for relabeling
    
    # Simulate what extract_multiple_files returns - keys are role names
    extracted_data = {
        'client': [
            {'type': 'h1', 'value': 'Client Heading', 'source': 'client'},
            {'type': 'p', 'value': 'Client paragraph', 'source': 'client'}
        ],
        'competitor': [
            {'type': 'h1', 'value': 'Competitor Heading', 'source': 'competitor'},
            {'type': 'p', 'value': 'Competitor paragraph', 'source': 'competitor'}
        ]
    }
    
    symbol_mapping = {
        "client": "circle",
        "competitor": "square",
        "Query": "x"
    }
    
    size_mapping = {
        "client": 10,
        "competitor": 8,
        "Query": 6
    }
    
    # Create a mock generator to avoid loading actual model
    with patch('passage_embed.analysis.embeddings.SentenceTransformer'):
        generator = EmbeddingGenerator(model_name='all-MiniLM-L6-v2')
        
        # Mock the encode methods to return predictable embeddings
        def mock_encode(texts):
            if isinstance(texts, list):
                return np.random.rand(len(texts), 384).astype(np.float32)
            return np.random.rand(384).astype(np.float32)
        
        generator.model.encode = Mock(side_effect=mock_encode)
        generator.model.encode_document = Mock(side_effect=mock_encode)
        
        # Process the data
        embeddings_data, mean_embeddings = generator.process_json_data(
            extracted_data, symbol_mapping, size_mapping
        )
        
        # Check that labels are role names (not URLs)
        labels = [data['label'] for data in embeddings_data]
        assert 'client' in labels
        assert 'competitor' in labels
        
        # Check that mean_embeddings keys are role names
        assert 'client' in mean_embeddings
        assert 'competitor' in mean_embeddings
        
        # Now simulate the relabeling logic from cli.py
        client_domain = 'example.com'
        competitor_domain = 'competitor.com'
        
        role_to_domain = {
            'client': client_domain,
            'competitor': competitor_domain
        }
        
        # Update labels
        for data in embeddings_data:
            if data['label'] in role_to_domain:
                data['label'] = role_to_domain[data['label']]
        
        # Update mean embeddings keys
        mean_embeddings_with_domains = {}
        for key, value in mean_embeddings.items():
            if key in role_to_domain:
                mean_embeddings_with_domains[role_to_domain[key]] = value
            else:
                mean_embeddings_with_domains[key] = value
        
        # Verify relabeling worked
        updated_labels = [data['label'] for data in embeddings_data]
        assert client_domain in updated_labels
        assert competitor_domain in updated_labels
        assert 'client' not in updated_labels
        assert 'competitor' not in updated_labels
        
        # Verify mean embeddings keys were updated
        assert client_domain in mean_embeddings_with_domains
        assert competitor_domain in mean_embeddings_with_domains
        assert 'client' not in mean_embeddings_with_domains
        assert 'competitor' not in mean_embeddings_with_domains
