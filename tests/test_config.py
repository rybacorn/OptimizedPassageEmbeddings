"""Tests for configuration management."""

import sys
from pathlib import Path
import yaml
import pytest
from unittest.mock import patch, mock_open

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from passage_embed.core.config import Config, ScrapingConfig, EmbeddingConfig, VisualizationConfig


def test_config_loads_with_nested_dataclasses(tmp_path):
    """Test that Config properly reconstructs nested dataclasses from YAML."""
    config_file = tmp_path / "config.yaml"
    
    config_data = {
        'output_dir': 'custom_outputs',
        'scraping': {
            'timeout': 60,
            'retry_attempts': 5
        },
        'embedding': {
            'model_name': 'custom-model',
            'embedding_dim': 512
        },
        'visualization': {
            'plot_height': 800,
            'plot_width': 1000
        }
    }
    
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)
    
    config = Config.load_from_file(str(config_file), interactive=False)
    
    # Check top-level field
    assert config.output_dir == 'custom_outputs'
    
    # Check nested dataclasses are properly reconstructed
    assert isinstance(config.scraping, ScrapingConfig)
    assert config.scraping.timeout == 60
    assert config.scraping.retry_attempts == 5
    
    assert isinstance(config.embedding, EmbeddingConfig)
    assert config.embedding.model_name == 'custom-model'
    assert config.embedding.embedding_dim == 512
    
    assert isinstance(config.visualization, VisualizationConfig)
    assert config.visualization.plot_height == 800
    assert config.visualization.plot_width == 1000


def test_config_loads_with_partial_overrides(tmp_path):
    """Test that Config allows partial overrides in YAML."""
    config_file = tmp_path / "config.yaml"
    
    # Only override some fields
    config_data = {
        'output_dir': 'partial_outputs',
        'embedding': {
            'model_name': 'partial-model'
            # embedding_dim not specified, should use default
        }
    }
    
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)
    
    config = Config.load_from_file(str(config_file), interactive=False)
    
    # Overridden field
    assert config.output_dir == 'partial_outputs'
    assert config.embedding.model_name == 'partial-model'
    
    # Default values should be preserved
    assert config.embedding.embedding_dim == 768  # default value
    assert isinstance(config.scraping, ScrapingConfig)  # default config
    assert config.scraping.timeout == 30  # default value


def test_config_handles_invalid_nested_config(tmp_path, monkeypatch):
    """Test that Config prompts user when nested config is invalid."""
    config_file = tmp_path / "config.yaml"
    
    # Invalid scraping config (timeout should be int, not string)
    config_data = {
        'scraping': {
            'timeout': 'invalid',  # Should be int
            'retry_attempts': 3
        }
    }
    
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)
    
    # Simulate user input 'n' (don't proceed)
    with patch('builtins.input', return_value='n'):
        with pytest.raises(ValueError, match="Config loading cancelled"):
            Config.load_from_file(str(config_file), interactive=True)
    
    # Simulate user input 'y' (proceed with defaults)
    with patch('builtins.input', return_value='y'):
        config = Config.load_from_file(str(config_file), interactive=True)
        # Should use default scraping config
        assert isinstance(config.scraping, ScrapingConfig)
        assert config.scraping.timeout == 30  # default value


def test_config_creates_default_when_file_missing(tmp_path):
    """Test that Config creates default config file when it doesn't exist."""
    config_file = tmp_path / "new_config.yaml"
    
    # File doesn't exist yet
    assert not config_file.exists()
    
    # Load should create default config
    config = Config.load_from_file(str(config_file), interactive=False)
    
    # File should now exist
    assert config_file.exists()
    
    # Should have default values
    assert config.output_dir == 'outputs'
    assert isinstance(config.scraping, ScrapingConfig)
    assert isinstance(config.embedding, EmbeddingConfig)


def test_config_validation_with_invalid_values(tmp_path):
    """Test that Config validation catches invalid values."""
    config_file = tmp_path / "config.yaml"
    
    # Invalid log_level
    config_data = {
        'log_level': 'INVALID_LEVEL'
    }
    
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)
    
    # With interactive=False, should raise error
    with pytest.raises(ValueError, match="Configuration validation failed"):
        Config.load_from_file(str(config_file), interactive=False)
    
    # With interactive=True, should prompt
    with patch('builtins.input', return_value='y'):
        config = Config.load_from_file(str(config_file), interactive=True)
        # Should proceed despite validation error


def test_config_empty_file_uses_defaults(tmp_path):
    """Test that empty YAML file uses all defaults."""
    config_file = tmp_path / "config.yaml"
    
    # Create empty config file
    with open(config_file, 'w') as f:
        yaml.dump({}, f)
    
    config = Config.load_from_file(str(config_file), interactive=False)
    
    # Should have all default values
    assert config.output_dir == 'outputs'
    assert config.embedding.model_name == 'google/embeddinggemma-300m'
    assert config.embedding.embedding_dim == 768
    assert isinstance(config.scraping, ScrapingConfig)
    assert isinstance(config.embedding, EmbeddingConfig)
    assert isinstance(config.visualization, VisualizationConfig)
