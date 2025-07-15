# 📁 Output Management System

## Overview

The Passage Embedding Analysis Tool now has a structured output management system that prevents scattered test outputs and organizes results consistently.

## Directory Structure

```
outputs/
├── test_runs/                    # All test outputs go here
│   ├── test_run_20250115_143022/ # Timestamped test runs
│   ├── test_run_20250115_150145/
│   └── consolidated_20250115_160000_test_output/ # Consolidated old outputs
└── production/                   # Production analysis outputs (future)
```

## Configuration

The system uses `config.yaml` to define output locations:

```yaml
# Output directory structure
output_dir: "outputs"
test_output_dir: "outputs/test_runs"
log_dir: "logs"
cache_dir: ".cache"
```

## CLI Commands

### Production Analysis
```bash
# Standard analysis - outputs to outputs/
passage-embed analyze \
  --client "https://client.com" \
  --competitor "https://competitor.com" \
  --queries "query1,query2,query3"
```

### Test Analysis
```bash
# Test analysis - outputs to outputs/test_runs/test_run_TIMESTAMP/
passage-embed test \
  --client "https://client.com" \
  --competitor "https://competitor.com" \
  --queries "query1,query2,query3"

# Named test run
passage-embed test \
  --client "https://client.com" \
  --competitor "https://competitor.com" \
  --queries "query1,query2,query3" \
  --run-name "heygen_vs_synthesia_test"
```

## Output Management Utilities

### Cleanup Script
```bash
# Show current output structure
python cleanup_test_outputs.py --show

# Clean up old test runs (older than 7 days)
python cleanup_test_outputs.py --cleanup

# Consolidate scattered outputs
python cleanup_test_outputs.py --consolidate

# Custom retention period
python cleanup_test_outputs.py --cleanup --keep-days 14
```

### Python API
```python
from src.passage_embed.utils.output_management import (
    get_output_directory,
    create_test_run_directory,
    cleanup_old_test_runs
)

# Get appropriate output directory
output_dir = get_output_directory(is_test=True)

# Create timestamped test run directory
test_dir = create_test_run_directory(run_name="my_test")

# Clean up old test runs
cleanup_old_test_runs(keep_days=7)
```

## File Naming Convention

All output files follow a consistent naming pattern:

- **HTML files**: `{role}-{domain}-{path}-v{n}.html`
- **JSON data**: `extracted_html_data-v{n}.json`
- **Visualizations**: `embedding_comparison-v{n}.html`

Examples:
- `client-heygen.com-avatars-v1.html`
- `competitor-synthesia.io-features-avatars-v1.html`
- `extracted_html_data-v1.json`
- `embedding_comparison-v1.html`

## Versioning

The system automatically versions files to prevent overwrites:
- If `client-heygen.com-avatars-v1.html` exists, the next file becomes `client-heygen.com-avatars-v2.html`
- Version numbers are managed automatically by the `VersionManager` class

## Best Practices

### For Development/Testing
1. Use the `test` command for all experimental runs
2. Use descriptive `--run-name` for important tests
3. Run cleanup regularly to prevent disk space issues
4. Review test outputs in `outputs/test_runs/` before moving to production

### For Production
1. Use the `analyze` command for final analysis
2. Outputs go directly to `outputs/` for easy access
3. Consider archiving important results outside the project directory

### For Team Collaboration
1. All test outputs are automatically excluded from git (via `.gitignore`)
2. Share specific test run directories by copying them
3. Use the cleanup script to maintain a clean workspace

## Migration from Old System

If you have scattered test outputs from before this system:

1. Run the consolidation script:
   ```bash
   python cleanup_test_outputs.py --consolidate
   ```

2. This will move files from:
   - `test_output/`
   - `test_output_fixed/`
   - `outputs/heygen_test/`
   - Other scattered directories

3. Files will be moved to `outputs/test_runs/consolidated_TIMESTAMP_ORIGINAL_DIR/`

## Troubleshooting

### "Permission denied" errors
- Ensure you have write permissions to the `outputs/` directory
- Check if any files are open in other applications

### Disk space issues
- Run cleanup regularly: `python cleanup_test_outputs.py --cleanup`
- Adjust retention period: `python cleanup_test_outputs.py --cleanup --keep-days 3`

### Missing outputs
- Check the correct output directory based on command used (`analyze` vs `test`)
- Verify the output directory exists and has proper permissions
- Check logs in `logs/` for error messages 