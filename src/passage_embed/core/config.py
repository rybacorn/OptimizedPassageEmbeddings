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
    model_name: str = 'google/embeddinggemma-300m'
    embedding_dim: int = 768
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
    def load_from_file(cls, config_path: Optional[str] = None, interactive: bool = True) -> 'Config':
        """Load configuration from YAML file.
        
        Args:
            config_path: Path to configuration file. If None, uses 'config.yaml'.
            interactive: If True, prompts user on validation errors. If False, raises exceptions.
            
        Returns:
            Config instance with loaded values.
        """
        if config_path is None:
            config_path = 'config.yaml'
        
        config_file = Path(config_path)
        
        if not config_file.exists():
            # Create default config
            config = cls()
            config.save_to_file(config_path)
            return config
        
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f) or {}
        
        # Create default config first
        config = cls()
        
        # Reconstruct nested dataclasses from dict data
        if 'scraping' in data and isinstance(data['scraping'], dict):
            try:
                config.scraping = ScrapingConfig(**data['scraping'])
                # Validate the created config object
                if not isinstance(config.scraping.timeout, int) or config.scraping.timeout <= 0:
                    raise ValueError(f"scraping.timeout must be a positive integer, got {config.scraping.timeout}")
            except (TypeError, ValueError) as e:
                error_msg = f"Invalid scraping config: {e}"
                if interactive:
                    response = input(f"⚠️  Warning: {error_msg}\nProceed with default scraping config? [y/n]: ")
                    if response.lower() != 'y':
                        raise ValueError(f"Config loading cancelled: {error_msg}")
                    # Use default scraping config
                    config.scraping = ScrapingConfig()
                else:
                    raise ValueError(error_msg)
        
        if 'embedding' in data and isinstance(data['embedding'], dict):
            try:
                config.embedding = EmbeddingConfig(**data['embedding'])
            except (TypeError, ValueError) as e:
                error_msg = f"Invalid embedding config: {e}"
                if interactive:
                    response = input(f"⚠️  Warning: {error_msg}\nProceed with default embedding config? [y/n]: ")
                    if response.lower() != 'y':
                        raise ValueError(f"Config loading cancelled: {error_msg}")
                    # Use default embedding config
                    config.embedding = EmbeddingConfig()
                else:
                    raise ValueError(error_msg)
        
        if 'visualization' in data and isinstance(data['visualization'], dict):
            try:
                config.visualization = VisualizationConfig(**data['visualization'])
            except (TypeError, ValueError) as e:
                error_msg = f"Invalid visualization config: {e}"
                if interactive:
                    response = input(f"⚠️  Warning: {error_msg}\nProceed with default visualization config? [y/n]: ")
                    if response.lower() != 'y':
                        raise ValueError(f"Config loading cancelled: {error_msg}")
                    # Use default visualization config
                    config.visualization = VisualizationConfig()
                else:
                    raise ValueError(error_msg)
        
        # Update top-level fields (allow partial overrides)
        for key in ['output_dir', 'test_output_dir', 'log_dir', 'cache_dir', 'log_level', 'log_format']:
            if key in data:
                try:
                    setattr(config, key, data[key])
                except (TypeError, ValueError) as e:
                    error_msg = f"Invalid value for {key}: {e}"
                    if interactive:
                        response = input(f"⚠️  Warning: {error_msg}\nProceed with default value? [y/n]: ")
                        if response.lower() != 'y':
                            raise ValueError(f"Config loading cancelled: {error_msg}")
                    else:
                        raise ValueError(error_msg)
        
        # Validate the final configuration
        try:
            config.validate()
        except ValueError as e:
            error_msg = f"Configuration validation failed: {e}"
            if interactive:
                response = input(f"⚠️  Warning: {error_msg}\nProceed anyway? [y/n]: ")
                if response.lower() != 'y':
                    raise ValueError(f"Config loading cancelled: {error_msg}")
            else:
                raise ValueError(error_msg)
        
        return config
    
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
                'embedding_dim': self.embedding.embedding_dim,
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