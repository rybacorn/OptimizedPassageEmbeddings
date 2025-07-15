# Optimized Passage Embeddings

A Python tool for analyzing and comparing passage embeddings using various similarity metrics.

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
# Clone the repository
git clone https://github.com/rybacorn/OptimizedPassageEmbeddings.git
cd OptimizedPassageEmbeddings

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Usage

### Basic Analysis

```bash
# Analyze client vs competitor content
passage-embed analyze \
  --client "https://www.heygen.com/avatars" \
  --competitor "https://www.synthesia.io/features/avatars" \
  --queries "ai video generator,free ai video generator,best ai video generator"
```

### Test Analysis

```bash
# Run analysis in test mode (organized output)
passage-embed test \
  --client "https://www.heygen.com/avatars" \
  --competitor "https://www.synthesia.io/features/avatars" \
  --queries "ai video generator,free ai video generator,best ai video generator" \
  --run-name "heygen_vs_synthesia_test"
```

## Development

```bash
# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run linting
ruff check .
```

## License

MIT 