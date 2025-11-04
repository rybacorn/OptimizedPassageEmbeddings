"""Command-line interface for passage embedding analysis."""

import argparse
import sys
from pathlib import Path
from typing import Any, List, Optional

from .core.logging import setup_logging, get_logger
from .core.config import Config
from .utils.validation import validate_url, validate_queries, extract_domain_name
from .utils.output_management import create_test_run_directory
from .analysis.scraper import WebScraper
from .analysis.extractor import HTMLExtractor
from .analysis.embeddings import EmbeddingGenerator
from .visualization.plotly_3d import create_3d_visualization


MODEL_PRESETS = {
    "fast": "all-MiniLM-L6-v2",
    "accurate": "all-mpnet-base-v2",
    "multilingual": "paraphrase-multilingual-mpnet-base-v2",
    "large": "sentence-transformers/all-roberta-large-v1",
}

VALID_EMBEDDING_DIMS = (128, 256, 512, 768)
DEFAULT_MODEL_NAME = "google/embeddinggemma-300m"
DEFAULT_EMBEDDING_DIM = 768


def resolve_model_name(name: Optional[str]) -> str:
    """Resolve preset aliases to full model identifiers."""
    if not name:
        return DEFAULT_MODEL_NAME
    return MODEL_PRESETS.get(name, name)


def resolve_embedding_dim(cli_value: Optional[int], config_value: Optional[int]) -> int:
    """Resolve embedding dimension with CLI taking precedence."""
    if cli_value is not None:
        return cli_value
    if config_value is not None:
        return config_value
    return DEFAULT_EMBEDDING_DIM


def get_embedding_config_value(config_obj: Any, key: str) -> Optional[Any]:
    """Safely extract embedding configuration values from dataclass or dict."""
    if config_obj is None:
        return None
    if isinstance(config_obj, dict):
        return config_obj.get(key)
    return getattr(config_obj, key, None)


def analyze_urls(client_url: str, competitor_url: str, queries: List[str], 
                output_dir: str = 'outputs', config_path: Optional[str] = None,
                model: Optional[str] = None, embedding_dim: Optional[int] = None) -> str:
    """Analyze client vs competitor content against target queries.
    
    Args:
        client_url: Client website URL
        competitor_url: Competitor website URL
        queries: List of target queries
        output_dir: Directory to save outputs
        config_path: Path to configuration file
        model: Optional model override from CLI
        embedding_dim: Optional embedding dimension override from CLI
        
    Returns:
        Path to the generated HTML visualization
    """
    logger = get_logger(__name__)
    
    # Setup logging and config
    setup_logging()
    config = Config.load_from_file(config_path) if config_path else Config()
    
    # Resolve model and embedding dimension priorities: CLI > config > defaults
    embedding_config = getattr(config, 'embedding', None)
    config_model = get_embedding_config_value(embedding_config, 'model_name')
    config_embedding_dim = get_embedding_config_value(embedding_config, 'embedding_dim')

    resolved_model = resolve_model_name(model or config_model)
    resolved_embedding_dim = resolve_embedding_dim(embedding_dim, config_embedding_dim)

    if resolved_embedding_dim not in VALID_EMBEDDING_DIMS:
        logger.warning(
            "Embedding dimension %s is not supported; defaulting to %s.",
            resolved_embedding_dim,
            DEFAULT_EMBEDDING_DIM,
        )
        resolved_embedding_dim = DEFAULT_EMBEDDING_DIM

    logger.info(f"Starting analysis: Client={client_url}, Competitor={competitor_url}")
    logger.info(f"Target queries: {queries}")
    logger.info("Using embedding model '%s' (dim=%s)", resolved_model, resolved_embedding_dim)
    
    # Step 1: Scrape URLs
    logger.info("Step 1: Scraping URLs...")
    scraper = WebScraper(output_dir)
    html_files = scraper.scrape_multiple_urls({
        'client': client_url,
        'competitor': competitor_url
    })
    
    # Step 2: Extract content
    logger.info("Step 2: Extracting content...")
    extractor = HTMLExtractor(output_dir)
    extracted_data = extractor.extract_multiple_files(html_files)
    
    # Save extracted data
    json_file = extractor.save_extracted_data(extracted_data)
    
    # Step 3: Generate embeddings
    logger.info("Step 3: Generating embeddings...")
    embedding_gen = EmbeddingGenerator(model_name=resolved_model, embedding_dim=resolved_embedding_dim)
    
    # Extract domain names for better labeling
    client_domain = extract_domain_name(client_url)
    competitor_domain = extract_domain_name(competitor_url)
    
    # Symbol and size mappings
    symbol_mapping = {
        "client": "circle",
        "competitor": "square",
        "Query": "x"
    }
    
    size_mapping = {
        "client": 10,
        "competitor": 8,
        "Query": 6
    }
    
    # Process content embeddings (labels will be role names: 'client', 'competitor')
    embeddings_data, mean_embeddings = embedding_gen.process_json_data(
        extracted_data, symbol_mapping, size_mapping
    )
    
    # Create mapping from role names to domain names
    role_to_domain = {
        'client': client_domain,
        'competitor': competitor_domain
    }
    
    # Update labels to use domain names instead of role names
    for data in embeddings_data:
        if data['label'] in role_to_domain:
            data['label'] = role_to_domain[data['label']]
    
    # Update mean embeddings keys to use domain names
    mean_embeddings_with_domains = {}
    for key, value in mean_embeddings.items():
        if key in role_to_domain:
            mean_embeddings_with_domains[role_to_domain[key]] = value
        else:
            mean_embeddings_with_domains[key] = value
    mean_embeddings = mean_embeddings_with_domains
    
    # Process query embeddings
    query_embeddings_data, queries_mean = embedding_gen.generate_query_embeddings(queries)
    
    # Step 4: Create visualization
    logger.info("Step 4: Creating 3D visualization...")
    output_file = create_3d_visualization(
        embeddings_data + query_embeddings_data,
        mean_embeddings,
        queries_mean,
        output_dir,
        client_url,
        competitor_url,
        model_name=resolved_model,
        embedding_dim=resolved_embedding_dim,
    )
    
    logger.info(f"Analysis complete! Visualization saved to: {output_file}")
    return output_file


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Passage Embedding Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis with comma-separated queries
  passage-embed analyze \\
    --client "https://www.heygen.com/avatars" \\
    --competitor "https://www.synthesia.io/features/avatars" \\
    --queries "ai video generator,free ai video generator,best ai video generator"

  # Analysis with query file
  passage-embed analyze \\
    --client "https://client.com/page" \\
    --competitor "https://competitor.com/page" \\
    --query-file "queries.txt"

  # Custom output directory
  passage-embed analyze \\
    --client "https://client.com" \\
    --competitor "https://competitor.com" \\
    --queries "query1,query2,query3" \\
    --output-dir "my_analysis"
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze", 
        help="Analyze client vs competitor content against target queries"
    )
    analyze_parser.add_argument(
        "--client", 
        required=True, 
        help="Client website URL"
    )
    analyze_parser.add_argument(
        "--competitor", 
        required=True, 
        help="Competitor website URL"
    )
    analyze_parser.add_argument(
        "--queries", 
        help="Comma-separated list of target queries"
    )
    analyze_parser.add_argument(
        "--query-file", 
        help="File containing target queries (one per line)"
    )
    analyze_parser.add_argument(
        "--output-dir", 
        default="outputs", 
        help="Output directory for results"
    )
    analyze_parser.add_argument(
        "--config", 
        help="Path to configuration file"
    )
    analyze_parser.add_argument(
        "--model",
        help="SentenceTransformer model or preset name (fast, accurate, multilingual, large)",
    )
    analyze_parser.add_argument(
        "--embedding-dim",
        type=int,
        choices=list(VALID_EMBEDDING_DIMS),
        help="Embedding dimension (128, 256, 512, 768). Applies Matryoshka truncation when supported.",
    )
    
    # Test run command
    test_parser = subparsers.add_parser(
        "test", 
        help="Run analysis in test mode with organized output"
    )
    test_parser.add_argument(
        "--client", 
        required=True, 
        help="Client website URL"
    )
    test_parser.add_argument(
        "--competitor", 
        required=True, 
        help="Competitor website URL"
    )
    test_parser.add_argument(
        "--queries", 
        help="Comma-separated list of target queries"
    )
    test_parser.add_argument(
        "--query-file", 
        help="File containing target queries (one per line)"
    )
    test_parser.add_argument(
        "--run-name", 
        help="Name for this test run (default: timestamp)"
    )
    test_parser.add_argument(
        "--config", 
        help="Path to configuration file"
    )
    test_parser.add_argument(
        "--model",
        help="SentenceTransformer model or preset name (fast, accurate, multilingual, large)",
    )
    test_parser.add_argument(
        "--embedding-dim",
        type=int,
        choices=list(VALID_EMBEDDING_DIMS),
        help="Embedding dimension (128, 256, 512, 768). Applies Matryoshka truncation when supported.",
    )
    
    # Legacy commands (for backward compatibility)
    legacy_analyze_parser = subparsers.add_parser(
        "legacy-analyze", 
        help="Legacy simple text similarity (deprecated)"
    )
    legacy_analyze_parser.add_argument(
        "--text1", 
        required=True, 
        help="First passage text"
    )
    legacy_analyze_parser.add_argument(
        "--text2", 
        required=True, 
        help="Second passage text"
    )
    
    embed_parser = subparsers.add_parser(
        "embed", 
        help="Generate embeddings for a text file (deprecated)"
    )
    embed_parser.add_argument(
        "--input", 
        required=True, 
        help="Input text file"
    )
    embed_parser.add_argument(
        "--output", 
        required=True, 
        help="Output embeddings file"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "analyze":
            # Validate URLs
            client_url = validate_url(args.client)
            competitor_url = validate_url(args.competitor)
            
            # Get queries
            queries = []
            if args.queries:
                queries = validate_queries(args.queries)
            elif args.query_file:
                query_file = Path(args.query_file)
                if not query_file.exists():
                    print(f"Error: Query file {args.query_file} not found")
                    sys.exit(1)
                with open(query_file, 'r') as f:
                    query_lines = [line.strip() for line in f if line.strip()]
                queries = validate_queries(','.join(query_lines))
            else:
                print("Error: Must provide either --queries or --query-file")
                sys.exit(1)
            
            # Run analysis
            output_file = analyze_urls(
                client_url, 
                competitor_url, 
                queries, 
                args.output_dir,
                args.config,
                model=args.model,
                embedding_dim=args.embedding_dim,
            )
            
            print(f"\n✅ Analysis complete!")
            print(f"📊 Visualization saved to: {output_file}")
            print(f"🌐 Open the HTML file in your browser to view the 3D visualization")
            
        elif args.command == "test":
            # Validate URLs
            client_url = validate_url(args.client)
            competitor_url = validate_url(args.competitor)
            
            # Get queries
            queries = []
            if args.queries:
                queries = validate_queries(args.queries)
            elif args.query_file:
                query_file = Path(args.query_file)
                if not query_file.exists():
                    print(f"Error: Query file {args.query_file} not found")
                    sys.exit(1)
                with open(query_file, 'r') as f:
                    query_lines = [line.strip() for line in f if line.strip()]
                queries = validate_queries(','.join(query_lines))
            else:
                print("Error: Must provide either --queries or --query-file")
                sys.exit(1)
            
            # Create test run directory
            config = Config.load_from_file(args.config) if args.config else Config()
            test_dir = create_test_run_directory(config, args.run_name)
            
            print(f"🧪 Test run directory: {test_dir}")
            
            # Run analysis in test mode
            output_file = analyze_urls(
                client_url, 
                competitor_url, 
                queries, 
                str(test_dir),
                args.config,
                model=args.model,
                embedding_dim=args.embedding_dim,
            )
            
            print(f"\n✅ Test analysis complete!")
            print(f"📊 Visualization saved to: {output_file}")
            print(f"📁 All test outputs saved to: {test_dir}")
            print(f"🌐 Open the HTML file in your browser to view the 3D visualization")
            
        elif args.command == "legacy-analyze":
            # Legacy simple text similarity
            print("Warning: This is a legacy command. Use 'analyze' for full content analysis.")
            similarity = 0.0  # Placeholder
            print(f"Similarity score: {similarity}")
            
        elif args.command == "embed":
            # Legacy embedding generation
            print("Warning: This is a legacy command. Use 'analyze' for full content analysis.")
            print("Embedding generation completed (placeholder)")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 