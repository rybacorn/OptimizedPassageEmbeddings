# Optimized Passage Embeddings

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.0-orange)](https://github.com/rybacorn/OptimizedPassageEmbeddings)

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

## Troubleshooting

### Common Issues

**"URL not found" errors**
- Check that your URLs are accessible
- Some sites block automated requests

**"No content extracted"**
- The site might use JavaScript to load content
- Try a different page or competitor

**Large file sizes**
- Results can be several MB due to HTML content
- Use the cleanup script to manage old test runs

### Getting Help

If you encounter issues:
1. Check the logs in the `logs/` directory
2. Try running in test mode first
3. Verify your URLs are accessible in a browser

## Development

### Running Tests
```bash
pytest
```

### Code Quality
```bash
ruff check .
pre-commit run --all-files
```

### Project Structure
```
src/passage_embed/
├── cli.py                   # Command-line interface
├── core/                    # Configuration, logging, exceptions
├── analysis/                # Web scraping, content extraction, embeddings
├── visualization/           # 3D plotting and charts
└── utils/                   # Validation, versioning, output management
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Version History

- **0.1.0** - Initial release with core functionality
  - Web scraping and content extraction
  - Embedding generation and similarity analysis
  - 3D visualization
  - CLI interface 
MIT 