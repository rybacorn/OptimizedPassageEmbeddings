"""Custom exceptions for passage embedding analysis."""


class PassageEmbedError(Exception):
    """Base exception for passage embedding analysis."""
    pass


class ValidationError(PassageEmbedError):
    """Raised when input validation fails."""
    pass


class ScrapingError(PassageEmbedError):
    """Raised when web scraping fails."""
    pass


class EmbeddingError(PassageEmbedError):
    """Raised when embedding generation fails."""
    pass


class VisualizationError(PassageEmbedError):
    """Raised when visualization generation fails."""
    pass


class ConfigurationError(PassageEmbedError):
    """Raised when configuration is invalid."""
    pass


class FileError(PassageEmbedError):
    """Raised when file operations fail."""
    pass


class NetworkError(PassageEmbedError):
    """Raised when network operations fail."""
    pass 