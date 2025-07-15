"""3D visualization module for passage embedding analysis."""

import numpy as np
import pandas as pd
from openTSNE import TSNE
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from typing import Dict, List, Any
import os

from ..core.exceptions import VisualizationError
from ..core.logging import get_logger
from ..utils.versioning import VersionManager

logger = get_logger(__name__)


def create_3d_visualization(
    embeddings_data: List[Dict[str, Any]],
    mean_embeddings: Dict[str, np.ndarray],
    queries_mean: np.ndarray,
    output_dir: str = 'outputs',
    client_url: str = '',
    competitor_url: str = ''
) -> str:
    """Create 3D visualization of embeddings.
    
    Args:
        embeddings_data: List of embedding data dictionaries
        mean_embeddings: Dictionary mapping sources to mean embeddings
        queries_mean: Mean embedding of all queries
        output_dir: Directory to save the visualization
        
    Returns:
        Path to the generated HTML file
    """
    try:
        # Step 1: Reduce dimensions with t-SNE
        logger.info("Reducing dimensions with t-SNE...")
        all_embeddings = np.array([data['embedding'] for data in embeddings_data])
        tsne = TSNE(n_components=3, perplexity=30, random_state=42)
        reduced_embeddings = tsne.fit(all_embeddings)
        
        # Add coordinates to data
        for i, data in enumerate(embeddings_data):
            data['x'], data['y'], data['z'] = reduced_embeddings[i]
        
        # Step 2: Calculate means in t-SNE space (correct approach)
        df = pd.DataFrame(embeddings_data)
        tsne_means = {}
        
        # Calculate mean for each unique label in t-SNE space
        for label in df['label'].unique():
            label_data = df[df['label'] == label]
            tsne_means[label] = np.array([
                label_data['x'].mean(),
                label_data['y'].mean(),
                label_data['z'].mean()
            ])
        
        # Step 3: Calculate cosine similarities (still use original embeddings for accuracy)
        cosine_similarities = {
            key: cosine_similarity([mean], [queries_mean])[0][0] 
            for key, mean in mean_embeddings.items()
        }
        
        # Step 4: Create DataFrame (already created above)
        
        # Create site comparison title
        if client_url and competitor_url:
            from ..utils.validation import extract_domain_name
            client_domain = extract_domain_name(client_url)
            competitor_domain = extract_domain_name(competitor_url)
            plot_title = f"Content Embedding Analysis: {client_domain} vs {competitor_domain} vs Queries"
        else:
            plot_title = "Content Embedding Analysis: Client vs Competitor vs Queries"
        
        # Step 5: Create 3D scatter plot
        fig = px.scatter_3d(
            df,
            x='x', y='y', z='z',
            color='label',
            symbol='symbol',
            size='size',
            hover_data={
                'type': True,
                'value': True,
                'label': False,
                'symbol': False,
                'size': False
            },
            title=plot_title
        )
        
        # Step 6: Add mean embedding points and arrows using t-SNE means
        # Define color mapping for different sources
        color_mapping = {
            'client': '#1f77b4',  # Blue
            'competitor': '#ff7f0e',  # Orange
            'Queries': '#2ca02c',  # Green
        }
        
        # Add mean points and arrows for each group using t-SNE means
        for label, tsne_mean in tsne_means.items():
            # Determine color based on label
            if label == 'Queries':
                mean_color = color_mapping['Queries']
                mean_symbol = 'diamond-open'
            elif 'client' in label.lower() or any(client_domain in label for client_domain in ['heygen', 'synthesia', 'runway']):
                mean_color = color_mapping['client']
                mean_symbol = 'diamond'
            elif 'competitor' in label.lower() or any(comp_domain in label for comp_domain in ['competitor', 'rival']):
                mean_color = color_mapping['competitor']
                mean_symbol = 'diamond'
            else:
                # Default to blue for first, orange for second based on order
                mean_color = color_mapping['client'] if list(tsne_means.keys()).index(label) == 0 else color_mapping['competitor']
                mean_symbol = 'diamond'
            
            # Add mean point
            fig.add_trace(
                go.Scatter3d(
                    x=[tsne_mean[0]], y=[tsne_mean[1]], z=[tsne_mean[2]],
                    mode='markers',
                    marker=dict(size=15, symbol=mean_symbol, color=mean_color),
                    name=f'Mean: {label}',
                    showlegend=True
                )
            )
            
            # Add arrows from each mean to queries mean (if not queries itself)
            if label != 'Queries' and 'Queries' in tsne_means:
                queries_tsne_mean = tsne_means['Queries']
                fig.add_trace(
                    go.Scatter3d(
                        x=[tsne_mean[0], queries_tsne_mean[0]],
                        y=[tsne_mean[1], queries_tsne_mean[1]],
                        z=[tsne_mean[2], queries_tsne_mean[2]],
                        mode='lines+markers',
                        line=dict(color=mean_color, width=3, dash='dot'),
                        marker=dict(size=2),
                        name=f'{label} → Queries',
                        showlegend=True
                    )
                )
        
        # Step 7: Create similarity scores visualization
        similarity_data = [
            {'Source': key, 'Cosine Similarity': value}
            for key, value in cosine_similarities.items()
        ]
        similarity_df = pd.DataFrame(similarity_data)
        
        similarity_fig = px.bar(
            similarity_df,
            x='Source',
            y='Cosine Similarity',
            title="Cosine Similarity Scores (Higher is Better)",
            color='Cosine Similarity',
            color_continuous_scale='RdYlGn'
        )
        
        # Create HTML title with site comparison
        if client_url and competitor_url:
            from ..utils.validation import extract_domain_name
            client_domain = extract_domain_name(client_url)
            competitor_domain = extract_domain_name(competitor_url)
            html_title = f"Content Embedding Analysis: {client_domain} vs {competitor_domain}"
            page_title = f"🎯 Content Embedding Analysis: {client_domain} vs {competitor_domain}"
        else:
            html_title = "Content Embedding Analysis Results"
            page_title = "🎯 Content Embedding Analysis Results"
        
        # Step 7: Combine visualizations
        combined_html = f"""
        <html>
        <head>
            <title>{html_title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .visualization {{ margin-bottom: 40px; }}
                .similarity-scores {{ margin-top: 30px; }}
                .score {{ font-size: 18px; margin: 10px 0; }}
                .score.good {{ color: green; }}
                .score.medium {{ color: orange; }}
                .score.poor {{ color: red; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{page_title}</h1>
                    <p>3D visualization of content similarity to target queries</p>
                </div>
                
                <div class="visualization">
                    <h2>📊 3D Content Embedding Visualization</h2>
                    <p>Interactive 3D plot showing how client and competitor content aligns with target queries.</p>
                    {fig.to_html(full_html=False, include_plotlyjs=True)}
                </div>
                
                <div class="similarity-scores">
                    <h2>📈 Similarity Scores</h2>
                    <p>Cosine similarity scores between content and query intent (higher is better):</p>
                    {similarity_fig.to_html(full_html=False, include_plotlyjs=False)}
                    
                    <div class="score-details">
                        <h3>📋 Detailed Scores:</h3>
        """
        
        # Add detailed scores with color coding
        for key, score in cosine_similarities.items():
            if score >= 0.7:
                score_class = "good"
                score_emoji = "🟢"
            elif score >= 0.5:
                score_class = "medium"
                score_emoji = "🟡"
            else:
                score_class = "poor"
                score_emoji = "🔴"
            
            combined_html += f"""
                        <div class="score {score_class}">
                            {score_emoji} <strong>{key}:</strong> {score:.3f}
                        </div>
            """
        
        combined_html += """
                    </div>
                    
                    <div class="interpretation">
                        <h3>💡 How to Interpret These Results:</h3>
                        <ul>
                            <li><strong>🟢 High Score (0.7+):</strong> Content is well-aligned with query intent</li>
                            <li><strong>🟡 Medium Score (0.5-0.7):</strong> Content has some alignment but room for improvement</li>
                            <li><strong>🔴 Low Score (&lt;0.5):</strong> Content needs significant optimization</li>
                        </ul>
                        
                        <h3>🎯 Next Steps:</h3>
                        <ul>
                            <li>Focus on content elements that are farthest from the query mean</li>
                            <li>Update titles, headings, and meta descriptions to better match query intent</li>
                            <li>Add content that bridges the gap between current content and target queries</li>
                            <li>Monitor improvements by running this analysis again after changes</li>
                        </ul>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Step 8: Save visualization
        version_manager = VersionManager(output_dir)
        output_file = version_manager.get_versioned_path("embedding_comparison", '.html')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(combined_html)
        
        logger.info(f"3D visualization saved to: {output_file}")
        
        # Print similarity scores to console
        print("\n📈 Similarity Scores (higher is better):")
        for key, score in cosine_similarities.items():
            if score >= 0.7:
                emoji = "🟢"
            elif score >= 0.5:
                emoji = "🟡"
            else:
                emoji = "🔴"
            print(f"  {emoji} {key}: {score:.3f}")
        
        return str(output_file)
        
    except Exception as e:
        raise VisualizationError(f"Failed to create 3D visualization: {e}")


def create_simple_visualization(embeddings_data: List[Dict[str, Any]], output_dir: str = 'outputs') -> str:
    """Create a simple 2D visualization (fallback option)."""
    try:
        df = pd.DataFrame(embeddings_data)
        
        fig = px.scatter(
            df,
            x='x', y='y',
            color='label',
            symbol='symbol',
            size='size',
            hover_data=['type', 'value'],
            title="Content Embedding Analysis (2D View)"
        )
        
        version_manager = VersionManager(output_dir)
        output_file = version_manager.get_versioned_path("embedding_analysis_2d", '.html')
        
        fig.write_html(output_file)
        return str(output_file)
        
    except Exception as e:
        raise VisualizationError(f"Failed to create simple visualization: {e}") 