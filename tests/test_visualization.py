"""Tests for visualization functionality."""

import sys
from pathlib import Path
import numpy as np
import pytest

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from passage_embed.visualization.plotly_3d import create_3d_visualization

# Import the constant directly from the module
import passage_embed.visualization.plotly_3d as plotly_module
MIN_SAMPLES_FOR_TSNE = plotly_module.MIN_SAMPLES_FOR_TSNE


def test_visualization_pca_fallback_for_small_samples(monkeypatch, tmp_path):
    """Test that PCA fallback is used when sample size is too small for t-SNE."""
    # Create minimal embeddings data (less than MIN_SAMPLES_FOR_TSNE)
    embeddings_data = [
        {
            'embedding': np.random.rand(768).astype(np.float32),
            'label': 'test',
            'type': 'h1',
            'value': 'Test',
            'symbol': 'circle',
            'size': 8
        },
        {
            'embedding': np.random.rand(768).astype(np.float32),
            'label': 'test',
            'type': 'h2',
            'value': 'Test 2',
            'symbol': 'circle',
            'size': 8
        }
    ]
    
    mean_embeddings = {
        'test': np.random.rand(768).astype(np.float32)
    }
    queries_mean = np.random.rand(768).astype(np.float32)
    
    # Mock the file writing to avoid actually creating HTML
    output_file = tmp_path / "test_output.html"
    
    # This should not raise an error and should use PCA
    result = create_3d_visualization(
        embeddings_data,
        mean_embeddings,
        queries_mean,
        str(tmp_path),
        client_url="https://test.com",
        competitor_url="https://competitor.com"
    )
    
    # Should have created the output file
    assert Path(result).exists()


def test_visualization_adaptive_perplexity(monkeypatch, tmp_path):
    """Test that adaptive perplexity is used for t-SNE."""
    # Create embeddings data with exactly the minimum samples
    n_samples = MIN_SAMPLES_FOR_TSNE
    embeddings_data = [
        {
            'embedding': np.random.rand(768).astype(np.float32),
            'label': 'test',
            'type': f'h{i}',
            'value': f'Test {i}',
            'symbol': 'circle',
            'size': 8
        }
        for i in range(n_samples)
    ]
    
    mean_embeddings = {
        'test': np.random.rand(768).astype(np.float32)
    }
    queries_mean = np.random.rand(768).astype(np.float32)
    
    # This should use t-SNE with adaptive perplexity
    result = create_3d_visualization(
        embeddings_data,
        mean_embeddings,
        queries_mean,
        str(tmp_path),
        client_url="https://test.com",
        competitor_url="https://competitor.com"
    )
    
    assert Path(result).exists()


def test_visualization_large_sample_size(monkeypatch, tmp_path):
    """Test visualization with a larger sample size that should use default perplexity."""
    # Create embeddings data larger than default perplexity
    n_samples = 50
    embeddings_data = [
        {
            'embedding': np.random.rand(768).astype(np.float32),
            'label': 'test' if i < 25 else 'other',
            'type': f'h{i % 6 + 1}',
            'value': f'Test {i}',
            'symbol': 'circle',
            'size': 8
        }
        for i in range(n_samples)
    ]
    
    mean_embeddings = {
        'test': np.random.rand(768).astype(np.float32),
        'other': np.random.rand(768).astype(np.float32)
    }
    queries_mean = np.random.rand(768).astype(np.float32)
    
    result = create_3d_visualization(
        embeddings_data,
        mean_embeddings,
        queries_mean,
        str(tmp_path),
        client_url="https://test.com",
        competitor_url="https://competitor.com"
    )
    
    assert Path(result).exists()
