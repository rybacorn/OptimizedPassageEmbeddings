"""Validation utilities for passage embedding analysis."""

import re
from pathlib import Path
from typing import List, Union
from urllib.parse import urlparse

from ..core.exceptions import ValidationError


def validate_url(url: str) -> str:
    """Validate and normalize a URL.
    
    Args:
        url: URL string to validate
        
    Returns:
        Normalized URL string
        
    Raises:
        ValidationError: If URL is invalid
    """
    if not url:
        raise ValidationError("URL cannot be empty")
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Basic URL validation
    try:
        result = urlparse(url)
        if not result.netloc:
            raise ValidationError(f"Invalid URL: {url}")
        return url
    except Exception as e:
        raise ValidationError(f"Invalid URL format: {url} - {e}")


def extract_domain_name(url: str) -> str:
    """Extract a clean domain name from a URL for display purposes.
    
    Args:
        url: URL string
        
    Returns:
        Clean domain name (e.g., "heygen.com" from "https://www.heygen.com/avatars")
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Remove port if present
        if ':' in domain:
            domain = domain.split(':')[0]
        
        return domain
    except Exception:
        # Fallback: return the original URL if parsing fails
        return url


def validate_queries(queries_str: str) -> List[str]:
    """Validate and parse comma-separated queries.
    
    Args:
        queries_str: Comma-separated query string
        
    Returns:
        List of validated query strings
        
    Raises:
        ValidationError: If queries are invalid
    """
    if not queries_str:
        raise ValidationError("Queries cannot be empty")
    
    queries = [q.strip() for q in queries_str.split(',') if q.strip()]
    
    if not queries:
        raise ValidationError("No valid queries found")
    
    if len(queries) > 50:
        raise ValidationError("Too many queries (maximum 50)")
    
    # Validate individual queries
    for i, query in enumerate(queries):
        if len(query) < 2:
            raise ValidationError(f"Query {i+1} too short: '{query}'")
        if len(query) > 200:
            raise ValidationError(f"Query {i+1} too long: '{query}'")
    
    return queries


def validate_role(role: str) -> str:
    """Validate a role name.
    
    Args:
        role: Role to validate
        
    Returns:
        Normalized role
        
    Raises:
        ValidationError: If role is invalid
    """
    valid_roles = ['client', 'competitor', 'comparison']
    
    if not role:
        raise ValidationError("Role cannot be empty")
    
    role = role.lower().strip()
    
    if role not in valid_roles:
        raise ValidationError(f"Invalid role: {role}. Must be one of: {valid_roles}")
    
    return role


def validate_output_directory(output_dir: Union[str, Path]) -> Path:
    """Validate and create output directory.
    
    Args:
        output_dir: Output directory path
        
    Returns:
        Path object for output directory
        
    Raises:
        ValidationError: If directory cannot be created
    """
    path = Path(output_dir)
    
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except Exception as e:
        raise ValidationError(f"Cannot create output directory {path}: {e}")


def validate_config_values(config: dict) -> None:
    """Validate configuration values.
    
    Args:
        config: Configuration dictionary
        
    Raises:
        ValidationError: If configuration is invalid
    """
    # Validate scraping config
    if 'scraping' in config:
        scraping = config['scraping']
        if 'timeout' in scraping and (not isinstance(scraping['timeout'], int) or scraping['timeout'] <= 0):
            raise ValidationError("scraping.timeout must be a positive integer")
        
        if 'retry_attempts' in scraping and (not isinstance(scraping['retry_attempts'], int) or scraping['retry_attempts'] < 0):
            raise ValidationError("scraping.retry_attempts must be a non-negative integer")
    
    # Validate embedding config
    if 'embedding' in config:
        embedding = config['embedding']
        if 'batch_size' in embedding and (not isinstance(embedding['batch_size'], int) or embedding['batch_size'] <= 0):
            raise ValidationError("embedding.batch_size must be a positive integer")
        
        if 'max_length' in embedding and (not isinstance(embedding['max_length'], int) or embedding['max_length'] <= 0):
            raise ValidationError("embedding.max_length must be a positive integer")
    
    # Validate logging config
    if 'log_level' in config:
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if config['log_level'] not in valid_levels:
            raise ValidationError(f"log_level must be one of: {valid_levels}") 