"""HTML content extraction module for passage embedding analysis."""

import json
from pathlib import Path
from typing import Dict, List, Any
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os

from ..core.exceptions import FileError
from ..core.logging import get_logger
from ..utils.versioning import VersionManager

logger = get_logger(__name__)


class HTMLExtractor:
    """HTML content extractor for SEO-relevant elements."""
    
    def __init__(self, output_dir: str = 'outputs'):
        """Initialize HTML extractor.
        
        Args:
            output_dir: Directory to save extracted data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.version_manager = VersionManager(output_dir)
    
    def extract_from_html(self, html_content: str, source_name: str) -> List[Dict[str, Any]]:
        """Extract SEO-relevant content from HTML.
        
        Args:
            html_content: HTML content as string
            source_name: Name/source of the HTML content
            
        Returns:
            List of extracted content items
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        extracted_data = []
        
        # Extract headings and meta tags
        for tag in ['title', 'meta[name="description"]', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            elements = soup.select(tag)
            for element in elements:
                if tag == 'meta[name="description"]':
                    text_value = element.attrs.get('content', '')
                else:
                    text_value = element.get_text(strip=True)
                
                if text_value:
                    extracted_data.append({
                        'type': tag.replace('meta[name="description"]', 'meta description'),
                        'value': text_value,
                        'source': source_name
                    })
        
        # Extract images inside <picture> tags
        for img in soup.select('picture img'):
            src = img.get('src')
            alt = img.get('alt')
            
            if src:
                filename = os.path.basename(urlparse(src).path)
                extracted_data.append({
                    'type': 'img src',
                    'value': filename,
                    'source': source_name
                })
            
            if alt:
                extracted_data.append({
                    'type': 'img alt',
                    'value': alt,
                    'source': source_name
                })
        
        # Extract <dt> and <dd> tags
        for dt in soup.find_all('dt'):
            text = dt.get_text(strip=True)
            if text:
                extracted_data.append({
                    'type': 'dt',
                    'value': text,
                    'source': source_name
                })
        
        for dd in soup.find_all('dd'):
            text = dd.get_text(strip=True)
            if text:
                extracted_data.append({
                    'type': 'dd',
                    'value': text,
                    'source': source_name
                })
        
        logger.info(f"Extracted {len(extracted_data)} elements from {source_name}")
        return extracted_data
    
    def extract_from_file(self, html_file: Path, source_name: str) -> List[Dict[str, Any]]:
        """Extract content from an HTML file.
        
        Args:
            html_file: Path to HTML file
            source_name: Name/source of the HTML content
            
        Returns:
            List of extracted content items
        """
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            return self.extract_from_html(html_content, source_name)
        except Exception as e:
            raise FileError(f"Failed to read HTML file {html_file}: {e}")
    
    def save_extracted_data(self, data: Dict[str, List[Dict[str, Any]]], base_name: str = "extracted_html_data") -> Path:
        """Save extracted data to JSON file.
        
        Args:
            data: Dictionary mapping sources to extracted data
            base_name: Base name for the output file
            
        Returns:
            Path to the saved JSON file
        """
        # Get versioned filename
        json_path = self.version_manager.get_versioned_path(base_name, '.json')
        
        # Save data
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Saved extracted data to: {json_path}")
        return json_path
    
    def extract_multiple_files(self, html_files: Dict[str, Path]) -> Dict[str, List[Dict[str, Any]]]:
        """Extract content from multiple HTML files.
        
        Args:
            html_files: Dictionary mapping roles to HTML file paths
            
        Returns:
            Dictionary mapping roles to extracted data
        """
        results = {}
        
        for role, html_file in html_files.items():
            try:
                extracted_data = self.extract_from_file(html_file, role)
                results[role] = extracted_data
            except Exception as e:
                logger.error(f"Failed to extract from {role} file: {e}")
                raise
        
        return results


def extract_html_content(html_files: Dict[str, Path], output_dir: str = 'outputs') -> Dict[str, List[Dict[str, Any]]]:
    """Convenience function to extract content from multiple HTML files.
    
    Args:
        html_files: Dictionary mapping roles to HTML file paths
        output_dir: Directory to save extracted data
        
    Returns:
        Dictionary mapping roles to extracted data
    """
    extractor = HTMLExtractor(output_dir)
    return extractor.extract_multiple_files(html_files) 