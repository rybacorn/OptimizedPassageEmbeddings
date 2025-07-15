"""Logging configuration for passage embedding analysis."""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logging(
    log_dir: str = 'logs',
    log_level: str = 'INFO',
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 7
) -> None:
    """Setup logging configuration.
    
    Args:
        log_dir: Directory to store log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format string for log messages
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
    """
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    log_file = log_path / f'passage_embed_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(getattr(logging, log_level.upper()))
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_log_file = log_path / f'passage_embed_errors_{datetime.now().strftime("%Y%m%d")}.log'
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class PerformanceLogger:
    """Context manager for logging operation performance."""
    
    def __init__(self, logger: logging.Logger, operation: str):
        """Initialize performance logger.
        
        Args:
            logger: Logger instance
            operation: Name of the operation being timed
        """
        self.logger = logger
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        """Start timing the operation."""
        self.start_time = datetime.now()
        self.logger.info(f"Starting {self.operation}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and log the duration."""
        if self.start_time:
            duration = datetime.now() - self.start_time
            if exc_type is None:
                self.logger.info(f"Completed {self.operation} in {duration.total_seconds():.2f}s")
            else:
                self.logger.error(f"Failed {self.operation} after {duration.total_seconds():.2f}s: {exc_val}")


def log_function_call(func):
    """Decorator to log function calls with performance timing."""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        with PerformanceLogger(logger, f"function {func.__name__}"):
            return func(*args, **kwargs)
    return wrapper 