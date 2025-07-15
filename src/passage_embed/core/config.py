"""Configuration management for passage embedding analysis."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class ScrapingConfig:
    """Configuration for web scraping."""
    user_agents: list[str] = field(default_factory=lambda: [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
    ])
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    rate_limit_delay: float = 1.0


@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""
    model_name: str = 'all-MiniLM-L6-v2'
    batch_size: int = 32
    max_length: int = 512
    cache_dir: str = '.cache/embeddings'


@dataclass
class VisualizationConfig:
    """Configuration for visualization."""
    plot_height: int = 600
    plot_width: int = 800
    dot_size: int = 8
    client_color: str = '#1f77b4'
    competitor_color: str = '#ff7f0e'
    comparison_color: str = '#2ca02c'


@dataclass
class Config:
    """Main configuration class."""
    
    # Paths
    output_dir: str = 'outputs'
    test_output_dir: str = 'outputs/test_runs'
    log_dir: str = 'logs'
    cache_dir: str = '.cache'
    
    # Scraping
    scraping: ScrapingConfig = field(default_factory=ScrapingConfig)
    
    # Embedding
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    
    # Visualization
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    
    # Logging
    log_level: str = 'INFO'
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @classmethod
    def load_from_file(cls, config_path: Optional[str] = None) -> 'Config':
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = 'config.yaml'
        
        config_file = Path(config_path)
        
        if not config_file.exists():
            # Create default config
            config = cls()
            config.save_to_file(config_path)
            return config
        
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)
        
        return cls(**data)
    
    def save_to_file(self, config_path: str = 'config.yaml') -> None:
        """Save configuration to YAML file."""
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict for YAML serialization
        config_dict = {
            'output_dir': self.output_dir,
            'test_output_dir': self.test_output_dir,
            'log_dir': self.log_dir,
            'cache_dir': self.cache_dir,
            'log_level': self.log_level,
            'log_format': self.log_format,
            'scraping': {
                'user_agents': self.scraping.user_agents,
                'timeout': self.scraping.timeout,
                'retry_attempts': self.scraping.retry_attempts,
                'retry_delay': self.scraping.retry_delay,
                'rate_limit_delay': self.scraping.rate_limit_delay
            },
            'embedding': {
                'model_name': self.embedding.model_name,
                'batch_size': self.embedding.batch_size,
                'max_length': self.embedding.max_length,
                'cache_dir': self.embedding.cache_dir
            },
            'visualization': {
                'plot_height': self.visualization.plot_height,
                'plot_width': self.visualization.plot_width,
                'dot_size': self.visualization.dot_size,
                'client_color': self.visualization.client_color,
                'competitor_color': self.visualization.competitor_color,
                'comparison_color': self.visualization.comparison_color
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2)
    
    def get_from_env(self, key: str, default: Any = None) -> Any:
        """Get configuration value from environment variable."""
        env_key = f'PASSAGE_EMBED_{key.upper()}'
        return os.getenv(env_key, default)
    
    def validate(self) -> None:
        """Validate configuration values."""
        if not isinstance(self.scraping.timeout, int) or self.scraping.timeout <= 0:
            raise ValueError("scraping.timeout must be a positive integer")
        
        if not isinstance(self.embedding.batch_size, int) or self.embedding.batch_size <= 0:
            raise ValueError("embedding.batch_size must be a positive integer")
        
        if self.log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            raise ValueError("log_level must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL") 