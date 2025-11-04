# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-11-04

### Added
- **PCA fallback for small datasets**: Visualization now automatically falls back to PCA when datasets have fewer than 4 samples, preventing crashes with sparse content
- **Adaptive perplexity calculation**: t-SNE now automatically adjusts perplexity based on sample size (capped at `min(30, n_samples - 1)`) for optimal performance
- **Interactive config validation**: Config loader now prompts users with `[y/n]` options when encountering invalid configuration values, allowing graceful degradation
- **Comprehensive test coverage**: Added 10 new tests covering visualization robustness, config loading, and domain relabeling fixes

### Fixed
- **t-SNE crash with small datasets**: Fixed `ValueError` that occurred when trying to run t-SNE on datasets with fewer samples than the default perplexity value (30)
- **Config YAML loading**: Fixed issue where nested dataclasses (`ScrapingConfig`, `EmbeddingConfig`, `VisualizationConfig`) were not properly reconstructed from YAML files, causing attribute access errors
- **Domain relabeling bug**: Fixed visualization labels not updating correctly - labels now properly map from role names ('client', 'competitor') to domain names in both embeddings data and mean embeddings
- **Package dependencies**: Fixed `pyproject.toml` missing critical dependencies (`numpy`, `pandas`, `openTSNE`, `torch`, `PyYAML`) and incorrect package name (`slugify` → `python-slugify`)

### Improved
- **Visualization robustness**: Visualization now handles edge cases gracefully, including datasets with as few as 1-2 samples
- **Config error handling**: Config loader provides clearer error messages and allows users to proceed with defaults when encountering invalid values
- **Partial config support**: Users can now override any configuration element without needing to specify all fields

### Changed
- **Default embedding model**: Already using `google/embeddinggemma-300m` as default (was previously `all-MiniLM-L6-v2`)
- **Visualization metadata**: Plot titles now indicate which dimensionality reduction method was used (t-SNE or PCA)

### Technical Details
- **Tests**: 17 tests total (7 existing + 10 new), all passing
- **Dependencies**: All dependencies now properly specified with version constraints in `pyproject.toml`
- **Backward compatibility**: All changes maintain backward compatibility with existing workflows

## [0.1.0] - 2024-10-30

### Initial Release
- Initial release with EmbeddingGemma support
- Web scraping and content extraction
- Embedding generation with Matryoshka Representation Learning (MRL) truncation
- 3D visualization with t-SNE dimensionality reduction
- CLI interface with model selection and embedding dimension options
- Configuration management via YAML files

[0.2.0]: https://github.com/rybacorn/OptimizedPassageEmbeddings/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/rybacorn/OptimizedPassageEmbeddings/releases/tag/v0.1.0
