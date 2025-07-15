# 🧠 Passage Embedding Analysis for Content Optimization

**Version**: v1
**Author**: Ryland Bacorn
**Delivery**: GitHub CLI tool (Python-based)
**Target Users**: SEO consultants, analysts, and content strategists
**Supported Environments**: macOS, Ubuntu, WSL (Linux terminal required)

---

## ✅ Objective

Compare semantic changes between original and updated webpage content using embeddings, measuring improvement toward fixed query intent. Enable client-vs-competitor benchmarking, visualize directional change, and support deeper SEO analysis.

---

## 🗱 System Architecture

```
[CLI] --> [Scraper] --> [HTML Saver] --> [Extractor] --> [Embedding Engine]
                               ↘                                ↓
                        [Versioned .html]               [Vector Store (in-memory)]
                               ↓                                ↓
                       [Versioned .json]  <---->  [Mean Cosine Comparator]
                                                           ↓
                                                 [3D Visualizer (.html)]
```

* **Entry Point**: Single CLI script
* **Modular Functions**:

  * Web Scraper
  * HTML Extractor
  * Embedding Calculator
  * Cosine Similarity Comparator
  * Plotly Visualizer
* **Third-party libraries**:

  * `requests`, `beautifulsoup4`, `lxml` – for scraping and parsing
  * `sentence-transformers` – for embeddings
  * `scikit-learn` – for cosine similarity
  * `plotly` – for visualization
  * `halo` – for CLI spinners
  * `argparse` – for CLI interface

---

## 🌟 Feature Requirements

### 1. Input Modes

* Accept **up to three URLs** via:

  * Positional order (client, competitor, comparison)
  * OR named flags (`--client`, `--competitor`, `--comparison`)
* Accept **query input** via:

  * `--queries` (comma-separated string)
  * OR `--query-file` (plain text file)

### 2. HTML Scraping

* Save each URL's HTML as `client-wicked-v1.html`, with:

  * Auto-incrementing version control
  * Naming pattern: `{role}-{slugified-page-title}-v{n}.html`
* Detect and reuse latest version number per role and slug
* Use user-agent headers and basic error retry logic for scraping

### 3. Content Extraction

* Elements extracted in **original HTML order**
* **Default tags**:

  * `<title>`
  * `<meta name="description">`
  * `<h1>` to `<h6>`
* **Optional extensions (via flags)**:

  * `<p>`, `<img>` `alt/src`, `<figcaption>`, `<dt>`, `<dd>`, `<article>`
* Output JSON format:

```json
[
  {"type": "title", "text": "Watch Wicked on Peacock"},
  {"type": "h1", "text": "Wicked: The Musical Comes Alive"},
  ...
]
```

### 4. Embedding

* Use SentenceTransformer (`all-MiniLM-L6-v2`, default)
* Generate one embedding per passage
* Compute **mean embedding vector** per page
* Embed query terms only once, store in a fixed anchor vector map

### 5. Comparison Logic

* Calculate cosine similarity between each page's **mean embedding** and each **query embedding**
* Store these results:

```json
{
  "client": {"query": "where to stream wicked", "similarity": 0.874},
  "competitor": {"query": "where to stream wicked", "similarity": 0.791},
  ...
}
```

* Directional arrows only plotted if mean vector changes

### 6. Visualization

* Output standalone interactive HTML (`embedding_comparison-v3.html`)
* Render:

  * Mean embedding points (original vs updated)
  * Arrows for movement
  * Fixed labeled query vectors
* Defaults:

  * Distinct color per source
  * Arrows as dashed lines
  * Labels using filenames
* Optional CLI styling:

  * `--label-mode`, `--dot-size`, `--client-color`, etc.

---

## 📂 Data Handling & Output

### File Output Summary

```
📁 ./outputs/
  ├— client-wicked-v1.html
  ├— client-wicked-v1.json
  ├— competitor-wicked-v1.html
  └— embedding_comparison-v1.html
```

### File Naming Rules

* HTML: `{role}-{slug}-v{n}.html`
* JSON: `{role}-{slug}-v{n}.json`
* HTML visualization: `embedding_comparison-v{n}.html`

### Directory Support

* All files saved in a consistent `outputs/` directory
* System will auto-detect latest version per role-slug combo

---

## 🚨 Error Handling Strategy

| Stage         | Potential Error   | Handling Strategy                    |
| ------------- | ----------------- | ------------------------------------ |
| Scraping      | Invalid URL       | Exit with helpful message            |
| Scraping      | 403/500 errors    | Retry with delay and log error       |
| Extraction    | Missing tags      | Insert empty `""` for passage        |
| Embedding     | Model not loading | Exit with spinner error              |
| Similarity    | Mismatched inputs | Validate and abort gracefully        |
| Visualization | Plot failure      | Write JSON log, skip chart if needed |

All major steps wrapped in **Halo spinners**, with clear success/failure messages in terminal output.

---

## ✅ CLI Example

```bash
python compare_embeddings.py \
  --client https://www.peacocktv.com/wicked \
  --competitor https://www.apple.com/tv/wicked \
  --queries "where to stream wicked, wicked trailer, wicked cast"
```

Optional flags:

```bash
--comparison https://www.netflix.com/title/12345 \
--query-file queries.txt \
--client-color "#0055ff" \
--label-mode filename \
--dot-size 5 \
--show-legend true
```

---

## 🧰 Testing Plan

### Unit Tests

* Scraper module with mock requests
* Extractor module with static test HTML
* Embedding module with fixed passage input
* Cosine similarity calculations with dummy vectors

### Integration Tests

* Full run with:

  * 3 URLs (client/competitor/comparison)
  * Known queries
  * Snapshot comparison of HTML, JSON, and HTML output

### Manual QA

* Test on real URLs (e.g., Wicked pages on Peacock & Apple)
* Check:

  * File outputs saved correctly
  * Visualization matches expected movement
  * Embeddings generated without errors
  * Arrows shown only if vectors changed

---

## 🔄 Iteration Notes (For Future Phases)

* [ ] Batch mode for scraping via CSV or URL list
* [ ] GSC integration to weight query importance
* [ ] Export similarity matrix as CSV
* [ ] Passage-level improvement ranking
* [ ] Theme-based query grouping (e.g., "cast", "trailer")
* [ ] Hugging Face Space interface (Gradio)
