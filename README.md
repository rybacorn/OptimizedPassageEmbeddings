<div align="center">
  <img src="OptimizedPassageEmbeddings.png" alt="Optimized Passage Embeddings Logo" width="300">
  
  # Optimized Passage Embeddings
  
  [![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Version](https://img.shields.io/badge/version-0.1.0-orange)](https://github.com/rybacorn/OptimizedPassageEmbeddings)
</div>

**Version:** 0.1.0

## What is this?

A Python tool that analyzes how well your website content matches against your competitors and target search queries. It scrapes web pages, extracts meaningful content, converts everything to embeddings, and creates interactive 3D visualizations showing how similar your content is to competitors and target keywords.

**Perfect for:** SEO analysis, content strategy, competitive research, and understanding how your web content aligns with search intent.

## Quick Start

### 1. Install

```bash
# Clone and install
git clone https://github.com/rybacorn/OptimizedPassageEmbeddings.git
cd OptimizedPassageEmbeddings
pip install -r requirements.txt
pip install -e .
```

### 2. Run Your First Analysis

```bash
# Compare your site vs a competitor
passage-embed analyze \
  --client "https://yoursite.com/your-page" \
  --competitor "https://competitor.com/their-page" \
  --queries "your target keyword,another keyword,third keyword"
```

### 3. View Results

Open the generated HTML file in your browser to see an interactive 3D visualization showing:
- How similar your content is to competitors
- How well your content matches target keywords
- Where you need to improve your content

## Usage Examples

### Basic Competitive Analysis
```bash
passage-embed analyze \
  --client "https://www.heygen.com/avatars" \
  --competitor "https://www.synthesia.io/features/avatars" \
  --queries "ai video generator,free ai video generator,best ai video generator"
```

### Test Mode (Organized Output)
```bash
# Creates timestamped folders for each test run
passage-embed test \
  --client "https://yoursite.com" \
  --competitor "https://competitor.com" \
  --queries "keyword1,keyword2,keyword3" \
  --run-name "my_analysis_test"
```

### Using Query Files
```bash
# Create a file called 'queries.txt' with one keyword per line
echo "ai video generator
free ai video generator
best ai video generator" > queries.txt

# Run analysis with the file
passage-embed analyze \
  --client "https://yoursite.com" \
  --competitor "https://competitor.com" \
  --query-file "queries.txt"
```

## What You Get

### Output Files
- **HTML visualization**: Interactive 3D plot showing content similarity
- **Extracted data**: JSON files with all scraped and processed content
- **Logs**: Detailed logs of the analysis process

### Visualization Features
- **3D scatter plot**: Each point represents a piece of content
- **Color coding**: Different colors for your content vs competitor vs keywords
- **Interactive**: Zoom, rotate, hover for details
- **Similarity scores**: See exactly how similar content pieces are

## Requirements

- Python 3.8 or higher
- Internet connection (for web scraping)
- Modern web browser (for viewing results)

## Installation

### Option 1: Quick Install
```bash
git clone https://github.com/rybacorn/OptimizedPassageEmbeddings.git
cd OptimizedPassageEmbeddings
pip install -r requirements.txt
pip install -e .
```

### Option 2: Development Setup
```bash
git clone https://github.com/rybacorn/OptimizedPassageEmbeddings.git
cd OptimizedPassageEmbeddings
pip install -r requirements.txt
pip install -r requirements-dev.txt
pip install -e .
pre-commit install
```

## How It Works

1. **Scraping**: Downloads HTML from your URLs and competitor URLs
2. **Extraction**: Pulls out meaningful content (headings, paragraphs, meta tags)
3. **Embedding**: Converts all text to numerical vectors using AI models
4. **Analysis**: Calculates similarity between your content, competitor content, and target keywords
5. **Visualization**: Creates an interactive 3D plot showing relationships

## Development

```bash
# Run tests
pytest

# Code quality
ruff check .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. 
MIT 