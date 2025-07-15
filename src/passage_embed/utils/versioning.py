"""File versioning utilities for passage embedding analysis."""

import re
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime


class VersionManager:
    """Manages file versioning for analysis outputs."""
    
    def __init__(self, output_dir: str = 'outputs'):
        """Initialize version manager.
        
        Args:
            output_dir: Directory to store versioned files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def get_next_version(self, base_name: str, extension: str) -> int:
        """Get the next version number for a file.
        
        Args:
            base_name: Base name of the file (without version)
            extension: File extension (including dot)
            
        Returns:
            Next version number
        """
        pattern = f"{base_name}-v(\\d+){extension}"
        existing_versions = []
        
        for file_path in self.output_dir.glob(f"{base_name}-v*{extension}"):
            match = re.match(pattern, file_path.name)
            if match:
                existing_versions.append(int(match.group(1)))
        
        return max(existing_versions, default=0) + 1
    
    def get_versioned_filename(self, base_name: str, extension: str) -> str:
        """Get the next versioned filename.
        
        Args:
            base_name: Base name of the file (without version)
            extension: File extension (including dot)
            
        Returns:
            Versioned filename
        """
        version = self.get_next_version(base_name, extension)
        return f"{base_name}-v{version}{extension}"
    
    def get_versioned_path(self, base_name: str, extension: str) -> Path:
        """Get the full path for the next versioned file.
        
        Args:
            base_name: Base name of the file (without version)
            extension: File extension (including dot)
            
        Returns:
            Full path to the versioned file
        """
        filename = self.get_versioned_filename(base_name, extension)
        return self.output_dir / filename
    
    def cleanup_old_versions(self, base_name: str, extension: str, keep_versions: int = 5) -> None:
        """Clean up old versions of a file.
        
        Args:
            base_name: Base name of the file (without version)
            extension: File extension (including dot)
            keep_versions: Number of recent versions to keep
        """
        pattern = f"{base_name}-v(\\d+){extension}"
        files_with_versions = []
        
        for file_path in self.output_dir.glob(f"{base_name}-v*{extension}"):
            match = re.match(pattern, file_path.name)
            if match:
                version = int(match.group(1))
                files_with_versions.append((version, file_path))
        
        # Sort by version number and keep only the most recent
        files_with_versions.sort(key=lambda x: x[0], reverse=True)
        
        for version, file_path in files_with_versions[keep_versions:]:
            file_path.unlink()
    
    def get_latest_version(self, base_name: str, extension: str) -> Optional[Path]:
        """Get the path to the latest version of a file.
        
        Args:
            base_name: Base name of the file (without version)
            extension: File extension (including dot)
            
        Returns:
            Path to the latest version, or None if no versions exist
        """
        pattern = f"{base_name}-v(\\d+){extension}"
        latest_version = None
        latest_number = -1
        
        for file_path in self.output_dir.glob(f"{base_name}-v*{extension}"):
            match = re.match(pattern, file_path.name)
            if match:
                version = int(match.group(1))
                if version > latest_number:
                    latest_number = version
                    latest_version = file_path
        
        return latest_version


def get_next_version(base_name: str, extension: str, output_dir: str = 'outputs') -> int:
    """Get the next version number for a file.
    
    Args:
        base_name: Base name of the file (without version)
        extension: File extension (including dot)
        output_dir: Directory to store versioned files
        
    Returns:
        Next version number
    """
    manager = VersionManager(output_dir)
    return manager.get_next_version(base_name, extension)


def create_versioned_filename(url: str, role: str, extension: str = '.html') -> str:
    """Create a versioned filename from a URL and role.
    
    Args:
        url: URL to create filename from
        role: Role of the URL (client, competitor, comparison)
        extension: File extension (including dot)
        
    Returns:
        Versioned filename
    """
    from slugify import slugify
    
    # Extract domain and path from URL
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '')
    path = parsed.path.strip('/')
    
    # Create base name
    if path:
        base_name = f"{role}-{domain}-{slugify(path)}"
    else:
        base_name = f"{role}-{domain}"
    
    return base_name 