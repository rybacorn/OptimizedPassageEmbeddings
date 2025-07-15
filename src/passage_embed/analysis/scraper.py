"""Web scraping module for passage embedding analysis."""

import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
from typing import Dict, List, Optional
from halo import Halo

from ..core.exceptions import ScrapingError, NetworkError
from ..core.logging import get_logger
from ..utils.validation import validate_url
from ..utils.versioning import VersionManager

logger = get_logger(__name__)


class WebScraper:
    """Web scraper for downloading HTML content."""
    
    def __init__(self, output_dir: str = 'outputs'):
        """Initialize web scraper.
        
        Args:
            output_dir: Directory to save downloaded HTML files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.version_manager = VersionManager(output_dir)
        
        # Default headers to avoid blocking
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }
    
    def scrape_url(self, url: str, role: str) -> Path:
        """Scrape a single URL and save the HTML.
        
        Args:
            url: URL to scrape
            role: Role of the URL (client, competitor, comparison)
            
        Returns:
            Path to the saved HTML file
            
        Raises:
            ScrapingError: If scraping fails
        """
        try:
            url = validate_url(url)
            logger.info(f"Scraping URL: {url}")
            
            with Halo(text=f"Downloading {role} HTML", spinner="dots") as spinner:
                response = requests.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                spinner.succeed(f"Downloaded {role} HTML")
            
            # Create filename from URL
            from urllib.parse import urlparse
            from slugify import slugify
            
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            path = parsed.path.strip('/')
            
            if path:
                base_name = f"{role}-{domain}-{slugify(path)}"
            else:
                base_name = f"{role}-{domain}"
            
            # Get versioned filename
            html_path = self.version_manager.get_versioned_path(base_name, '.html')
            
            # Save HTML
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            logger.info(f"Saved HTML to: {html_path}")
            return html_path
            
        except requests.RequestException as e:
            raise NetworkError(f"Failed to scrape {url}: {e}")
        except Exception as e:
            raise ScrapingError(f"Error scraping {url}: {e}")
    
    def scrape_multiple_urls(self, urls: Dict[str, str]) -> Dict[str, Path]:
        """Scrape multiple URLs.
        
        Args:
            urls: Dictionary mapping roles to URLs
            
        Returns:
            Dictionary mapping roles to file paths
        """
        results = {}
        
        for role, url in urls.items():
            try:
                html_path = self.scrape_url(url, role)
                results[role] = html_path
            except Exception as e:
                logger.error(f"Failed to scrape {role} URL: {e}")
                raise
        
        return results
    
    def get_html_content(self, file_path: Path) -> str:
        """Get HTML content from a saved file.
        
        Args:
            file_path: Path to HTML file
            
        Returns:
            HTML content as string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise ScrapingError(f"Failed to read HTML file {file_path}: {e}")


def scrape_urls(urls: Dict[str, str], output_dir: str = 'outputs') -> Dict[str, Path]:
    """Convenience function to scrape multiple URLs.
    
    Args:
        urls: Dictionary mapping roles to URLs
        output_dir: Directory to save HTML files
        
    Returns:
        Dictionary mapping roles to file paths
    """
    scraper = WebScraper(output_dir)
    return scraper.scrape_multiple_urls(urls) 