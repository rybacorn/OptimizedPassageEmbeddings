# Setup Guide for OptimizedPassageEmbeddings

This guide provides step-by-step instructions for installing and running OptimizedPassageEmbeddings.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Internet connection (for downloading dependencies and scraping web pages)

## Installation Methods

### Method 1: Automated Setup (Recommended)

The easiest way to get started is using the automated setup script:

```bash
cd OptimizedPassageEmbeddings
chmod +x setup.sh
./setup.sh
```

The script will:
1. ✅ Install all required dependencies
2. ✅ Install the package in development mode
3. ✅ Verify the `passage-embed` command works
4. ✅ Show you exactly what to do next

---

### Method 2: Manual Installation

If you prefer to install manually or the automated script fails:

#### Step 1: Install Dependencies

```bash
cd OptimizedPassageEmbeddings
pip install -r requirements.txt
```

**Note:** This includes all necessary packages including:
- `openTSNE` (for dimensionality reduction)
- `sentence-transformers` (for embeddings)
- `plotly` (for visualizations)
- `beautifulsoup4` (for web scraping)
- And more...

#### Step 2: Install the Package

```bash
pip install -e .
```

The `-e` flag installs in "editable" mode, which means you can modify the source code and changes take effect immediately.

#### Step 3: Verify Installation

```bash
passage-embed --help
```

**Expected Output:**
```
usage: passage-embed [-h] {analyze,test,legacy-analyze,embed} ...

Passage Embedding Analysis Tool

positional arguments:
  {analyze,test,legacy-analyze,embed}
                        Available commands
...
```

**If you see "command not found":**
- Check if your Python bin directory is in your PATH
- Try: `python -m src.passage_embed.cli --help` instead
- Consider using Method 3 below

---

### Method 3: Run Without Installing

If installation doesn't work, you can run the tool directly:

```bash
cd OptimizedPassageEmbeddings

# First, install dependencies
pip install -r requirements.txt

# Then run directly
python -m src.passage_embed.cli analyze \
  --client "https://yoursite.com" \
  --competitor "https://competitor.com" \
  --query-file "path/to/queries.txt"
```

---

## Common Installation Issues

### Issue 1: `ModuleNotFoundError: No module named 'openTSNE'`

**Solution:** The dependency is missing. Update requirements.txt or install manually:
```bash
pip install openTSNE
```

### Issue 2: `passage-embed: command not found`

**Causes:**
- The package wasn't installed with `pip install -e .`
- Your Python bin directory isn't in PATH

**Solutions:**
1. Verify you ran `pip install -e .` from the OptimizedPassageEmbeddings directory
2. Check which Python you're using: `which python` or `which python3`
3. Try the full path: `python -m src.passage_embed.cli` instead

### Issue 3: Permission Errors on macOS/Linux

**Solution:** Don't use `sudo`. Instead, install in user space:
```bash
pip install --user -r requirements.txt
pip install --user -e .
```

### Issue 4: Virtual Environment Issues

**Recommended:** Use a virtual environment to avoid conflicts:
```bash
cd OptimizedPassageEmbeddings
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

---

## Quick Start Guide

### 1. Prepare Your Data

Create a `queries.txt` file with one search query per line:
```
ai video generator
best ai video generator
free ai video generator
video creation software
digital avatars
```

### 2. Run Your First Analysis

**Option A: Using installed command**
```bash
passage-embed analyze \
  --client "https://yoursite.com/page" \
  --competitor "https://competitor.com/page" \
  --query-file "queries.txt"
```

**Option B: Using inline queries**
```bash
passage-embed analyze \
  --client "https://yoursite.com/page" \
  --competitor "https://competitor.com/page" \
  --queries "keyword1,keyword2,keyword3"
```

**Option C: Test mode with organized output**
```bash
passage-embed test \
  --client "https://yoursite.com/page" \
  --competitor "https://competitor.com/page" \
  --query-file "queries.txt" \
  --run-name "my_first_test"
```

### 3. View Results

After the analysis completes, you'll see:
```
✅ Analysis complete!
📊 Visualization saved to: outputs/embedding_visualization.html
🌐 Open the HTML file in your browser to view the 3D visualization
```

Simply open the HTML file in any modern browser to explore the interactive 3D plot.

---

## Understanding Output Files

### Default Output Directory: `outputs/`

When you run `analyze`, the following files are created:

```
outputs/
├── embedding_visualization.html    # Interactive 3D plot (MAIN OUTPUT)
├── extracted_data.json             # All scraped content in JSON format
├── client_DOMAIN.html              # Raw HTML from client site
├── competitor_DOMAIN.html          # Raw HTML from competitor site
└── passage_embedding_analysis.log  # Detailed execution logs
```

### Test Mode Output: `test_runs/TIMESTAMP_NAME/`

When you run `test`, outputs are organized by timestamp:

```
test_runs/
└── 20231030_143022_my_first_test/
    ├── embedding_visualization.html
    ├── extracted_data.json
    ├── client_DOMAIN.html
    ├── competitor_DOMAIN.html
    └── passage_embedding_analysis.log
```

---

## Command Reference

### Analyze Command

```bash
passage-embed analyze \
  --client "URL" \
  --competitor "URL" \
  [--queries "comma,separated,queries"] \
  [--query-file "path/to/file.txt"] \
  [--output-dir "custom_output"] \
  [--config "config.json"]
```

**Required:**
- `--client`: Your website URL
- `--competitor`: Competitor website URL
- `--queries` OR `--query-file`: Target search queries

**Optional:**
- `--output-dir`: Custom output directory (default: `outputs`)
- `--config`: Path to custom configuration file

### Test Command

Same as analyze, but with organized timestamped output:

```bash
passage-embed test \
  --client "URL" \
  --competitor "URL" \
  --query-file "queries.txt" \
  [--run-name "test_name"]
```

**Additional Options:**
- `--run-name`: Custom name for this test run (default: timestamp only)

---

## Real-World Example

```bash
# 1. Create your queries file
cat > queries.txt << EOF
ai video generator
free ai video generator
best ai video generator
ai avatar creator
text to video ai
EOF

# 2. Run the analysis
passage-embed analyze \
  --client "https://www.heygen.com/avatars" \
  --competitor "https://www.synthesia.io/features/avatars" \
  --query-file "queries.txt" \
  --output-dir "heygen_vs_synthesia"

# 3. Open the result
open heygen_vs_synthesia/embedding_visualization.html  # macOS
# Or: xdg-open heygen_vs_synthesia/embedding_visualization.html  # Linux
# Or: start heygen_vs_synthesia/embedding_visualization.html  # Windows
```

---

## What the Visualization Shows

The 3D interactive plot displays:

- **🔵 Blue Circles** = Your client's content pieces
- **🟥 Red Squares** = Competitor's content pieces
- **❌ X Marks** = Target search queries
- **Lines** = Connect each brand's content to their mean embedding

**How to Use:**
- **Zoom**: Scroll wheel or pinch
- **Rotate**: Click and drag
- **Hover**: See full text of each point
- **Click**: Select/highlight specific points

**What to Look For:**
- Points close together = similar content
- Your content near query marks = good keyword alignment
- Competitor content far from queries = opportunity for you
- Clusters = related topics/themes

---

## Troubleshooting Runtime Errors

### Error: "Failed to scrape URL"

**Causes:**
- Website blocking automated requests
- Invalid URL
- Network connectivity issues

**Solutions:**
1. Verify the URL is accessible in your browser
2. Check for typos in the URL
3. Some sites block scrapers - try a different page
4. Check your internet connection

### Error: "No content extracted"

**Causes:**
- Page has no readable text content
- Content is loaded dynamically with JavaScript

**Solutions:**
1. Try a different page with more static content
2. Check if the page loads properly in a browser
3. Some single-page apps won't work well with this tool

### Error: Embedding generation fails

**Causes:**
- Insufficient memory
- GPU issues (if using GPU acceleration)

**Solutions:**
1. Close other applications to free up RAM
2. Try with smaller content (fewer/shorter pages)
3. Check if `sentence-transformers` model downloads successfully

---

## Advanced Configuration

Create a `config.json` file for custom settings:

```json
{
  "embedding_model": "all-MiniLM-L6-v2",
  "tsne_perplexity": 30,
  "tsne_n_iter": 1000,
  "output_directory": "custom_outputs",
  "test_runs_directory": "my_test_runs"
}
```

Use it with:
```bash
passage-embed analyze \
  --client "URL" \
  --competitor "URL" \
  --queries "keywords" \
  --config "config.json"
```

---

## Performance Tips

1. **Use specific pages**: Analyze individual product/service pages rather than homepages
2. **Focused queries**: 5-20 highly relevant queries work better than 100 generic ones
3. **Content-rich pages**: Pages with substantial text content yield better results
4. **Test mode**: Use test runs to iterate and compare different URL combinations

---

## Getting Help

If you encounter issues:

1. **Check the logs**: Look at `passage_embedding_analysis.log` in the output directory
2. **Verify dependencies**: Run `pip list | grep -E "openTSNE|sentence-transformers|plotly"`
3. **Try the examples**: Start with the provided example URLs to verify installation
4. **Check Python version**: `python --version` (must be 3.8+)

---

## Next Steps

Once you have a working installation:

1. ✅ Run the example analysis to verify everything works
2. ✅ Prepare your target URLs and search queries
3. ✅ Run your first real analysis
4. ✅ Explore the 3D visualization
5. ✅ Iterate and refine your content strategy based on insights

Happy analyzing! 🚀

