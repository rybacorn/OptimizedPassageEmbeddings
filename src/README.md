# Passage Embedding Analysis - Source Code

This directory contains the core Python package for passage embedding analysis.

## Package Structure

```
src/passage_embed/
├── __init__.py              # Package initialization
├── cli.py                   # Command-line interface
├── core/                    # Core functionality
│   ├── __init__.py
│   ├── config.py           # Configuration management
│   ├── exceptions.py       # Custom exceptions
│   └── logging.py          # Logging system
├── analysis/               # Analysis modules
│   ├── __init__.py
│   ├── scraper.py          # Web scraping
│   ├── extractor.py        # HTML content extraction
│   └── embeddings.py       # Embedding generation
├── visualization/          # Visualization modules
│   ├── __init__.py
│   └── plotly_3d.py        # 3D visualization
└── utils/                  # Utility functions
    ├── __init__.py
    ├── validation.py       # Input validation
    ├── versioning.py       # File versioning
    └── output_management.py # Output directory management
```

## Installation

```bash
# Install in development mode
pip install -e .

# Or install dependencies only
pip install -r requirements.txt
```

## Usage

```bash
# Basic analysis
passage-embed analyze \
  --client "https://client.com" \
  --competitor "https://competitor.com" \
  --queries "query1,query2,query3"

# Test analysis (organized output)
passage-embed test \
  --client "https://client.com" \
  --competitor "https://competitor.com" \
  --queries "query1,query2,query3"
```

See the main [README.md](../README.md) for full documentation. 