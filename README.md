# Passage Embedding Analysis

A Python tool for analyzing and comparing passage embeddings using various similarity metrics.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/passage-embedding-analysis.git
cd passage-embedding-analysis

# Install dependencies
pip install -r requirements.txt --no-cache-dir --use-pep517

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

### Output Management

```bash
# Show current output structure
python cleanup_test_outputs.py --show

# Clean up old test runs
python cleanup_test_outputs.py --cleanup

# Consolidate scattered outputs
python cleanup_test_outputs.py --consolidate
```

For detailed output management information, see [OUTPUT_MANAGEMENT.md](OUTPUT_MANAGEMENT.md).

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