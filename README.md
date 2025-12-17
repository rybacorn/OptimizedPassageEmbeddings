<div align="center">
  <img src="OptimizedPassageEmbeddings.png" alt="Optimized Passage Embeddings Logo" width="300">
  
  # Optimized Passage Embeddings
  
  [![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Version](https://img.shields.io/badge/version-0.2.0-orange)](https://github.com/rybacorn/OptimizedPassageEmbeddings)
</div>

**Version:** 0.2.0

## What is this?

A Python tool that analyzes how well your website content matches against target search queries (and optionally compares against competitors). It scrapes web pages, extracts SEO-relevant content, converts everything to embeddings, and creates interactive 3D visualizations showing how similar your content is to target keywords and competitors (if provided).

**Perfect for:** SEO analysis, content strategy, competitive research, and understanding how your web content aligns with search intent.

## Quick Start

### 1. Install

> Prefer a guided walkthrough (including the automated `setup.sh` script)? Head over to [SETUP.md](SETUP.md) for the full setup guide.

#### Option A: Automated Setup (recommended)

```bash
git clone https://github.com/rybacorn/OptimizedPassageEmbeddings.git
cd OptimizedPassageEmbeddings
chmod +x setup.sh
./setup.sh
```

#### Option B: Manual Installation

```bash
# Clone and install
git clone https://github.com/rybacorn/OptimizedPassageEmbeddings.git
cd OptimizedPassageEmbeddings
pip install -r requirements.txt
pip install -e .
```

### 2. Run Your First Analysis

```bash
# Analyze your site against target queries (competitor optional)
passage-embed analyze \
  --client "https://yoursite.com/your-page" \
  --queries "your target keyword,another keyword,third keyword"

# Or compare your site vs a competitor
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

### Basic Analysis (No Competitor)
```bash
passage-embed analyze \
  --client "https://www.heygen.com/avatars" \
  --queries "ai video generator,free ai video generator,best ai video generator"
```

### Competitive Analysis
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
  --queries "keyword1,keyword2,keyword3" \
  --run-name "my_analysis_test"

# With competitor comparison
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

# Run analysis with the file (competitor optional)
passage-embed analyze \
  --client "https://yoursite.com" \
  --query-file "queries.txt"

# With competitor
passage-embed analyze \
  --client "https://yoursite.com" \
  --competitor "https://competitor.com" \
  --query-file "queries.txt"
```

### How to Get a Clean Query List of 50 Useful Queries

To get the most effective query list for your analysis, we recommend a two-step process:

#### Step 1: Gather Initial Queries from SEO Tools

Start by exporting keywords from Search Engine Optimization (SEO) tools like:
- **Semrush**: Use the Keyword Magic Tool or Organic Research to export keyword lists
- **Ahrefs**: Use Keywords Explorer to find relevant keywords and export them

Export a larger set (100-200 keywords) to give yourself options for filtering.

#### Step 2: Refine with Cosine Similarity Analysis

Once you have your initial keyword list, use the [SEO Keyword Similarity Tool on Hugging Face](https://huggingface.co/spaces/ReithBjarkan/SEO_Keyword_Similarity_Tool) to:
1. Upload your keyword list
2. Identify the most semantically related queries
3. Filter down to the top 50 most relevant and related queries

This cosine similarity analysis helps you:
- Remove duplicate or near-duplicate queries
- Identify the most cohesive set of related keywords
- Ensure your query list represents a focused topic cluster

#### Why This Approach?

A well-curated list of 50 semantically related queries will give you more meaningful analysis results than a random mix of keywords. The cosine similarity tool helps ensure your queries are actually related to each other, which makes the embedding analysis more accurate and actionable.

> **Note:** This query refinement feature may be integrated directly into the tool in the future.

### Choosing Embedding Models
```bash
# Use a preset alias
passage-embed analyze \
  --client "https://yoursite.com" \
  --queries "keyword1,keyword2" \
  --model multilingual

# Use a specific SentenceTransformers model id
passage-embed analyze \
  --client "https://yoursite.com" \
  --queries "keyword1,keyword2" \
  --model "sentence-transformers/all-mpnet-base-v2"

# Control Matryoshka (MRL) truncation when using EmbeddingGemma
passage-embed analyze \
  --client "https://yoursite.com" \
  --queries "keyword1,keyword2" \
  --model google/embeddinggemma-300m \
  --embedding-dim 256
```

**Available presets:**
- `fast` → `all-MiniLM-L6-v2`
- `accurate` → `all-mpnet-base-v2`
- `multilingual` → `paraphrase-multilingual-mpnet-base-v2`
- `large` → `sentence-transformers/all-roberta-large-v1`

### Hugging Face login (required for EmbeddingGemma)

The default model `google/embeddinggemma-300m` is gated. Run these once per machine:

```bash
# 1) Log in (prompts for your token or opens a browser)
huggingface-cli login

# Or export your token for the current shell
export HUGGINGFACE_HUB_TOKEN=hf_your_token_here

# 2) (Optional) warm the cache so the first CLI run is faster
python - <<'PY'
from sentence_transformers import SentenceTransformer
SentenceTransformer('google/embeddinggemma-300m')
PY
```

Prefer to stay on an open model? Override the defaults:

```bash
passage-embed analyze \
  --client "https://yoursite.com" \
  --queries "keyword1,keyword2" \
  --model fast
```

## What You Get

### Output Files
- **HTML visualization**: Interactive 3D plot showing content similarity
- **Extracted data**: JSON files with all scraped and processed content
- **Logs**: Detailed logs of the analysis process

### Visualization Features
- **3D scatter plot**: Each point represents a piece of content
- **Color coding**: Different colors for your content vs competitor vs keywords
- **Consistent query colors**: "Queries" and "Mean: Queries" use the same color for clarity
- **Interactive**: Zoom, rotate, hover for details
- **Similarity scores**: Compact bar chart showing cosine similarity scores
- **Extracted HTML elements table**: View all extracted content (titles, headings, meta tags) in a clean table
- **Robust dimensionality reduction**: Automatically uses PCA fallback for small datasets (< 4 samples)
- **Adaptive t-SNE**: Automatically adjusts perplexity based on dataset size for optimal performance

## Requirements

- Python 3.8 or higher
- Internet connection (for web scraping)
- Modern web browser (for viewing results)
- PyTorch 2.0+ (installed via `requirements.txt`) for EmbeddingGemma support

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

1. **Scraping**: Downloads HTML from your URL (and optionally a competitor URL)
2. **Extraction**: Pulls out SEO-relevant content:
   - Page title and meta description
   - Headings (h1-h6)
   - Image alt text and filenames (from `<picture>` tags)
   - Definition lists (dt/dd tags)
3. **Embedding**: Converts all text to numerical vectors using AI models (default: `google/embeddinggemma-300m` with optional Matryoshka truncation)
4. **Analysis**: Calculates similarity between your content, competitor content (if provided), and target keywords
5. **Visualization**: Creates an interactive 3D plot showing relationships with:
   - Consistent color coding for queries
   - Compact similarity score charts
   - Complete table of extracted HTML elements

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