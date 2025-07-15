#!/usr/bin/env python3
"""
Quick Analysis Script - Integrates existing functionality into a working CLI tool
Based on the PeacockExamples code that's already working.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from openTSNE import TSNE
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics.pairwise import cosine_similarity
from halo import Halo
import plotly.io as pio
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
from slugify import slugify


def scrape_url(url: str, role: str, output_dir: str = 'outputs') -> str:
    """Scrape a URL and save HTML."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    
    with Halo(text=f"Downloading {role} HTML", spinner="dots") as spinner:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        spinner.succeed(f"Downloaded {role} HTML")
    
    # Create filename
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '')
    path = parsed.path.strip('/')
    
    if path:
        base_name = f"{role}-{domain}-{slugify(path)}"
    else:
        base_name = f"{role}-{domain}"
    
    # Version the file
    version = 1
    html_file = f"{output_dir}/{base_name}-v{version}.html"
    while os.path.exists(html_file):
        version += 1
        html_file = f"{output_dir}/{base_name}-v{version}.html"
    
    # Save HTML
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print(f"Saved {role} HTML to: {html_file}")
    return html_file


def extract_html_content(html_file: str, source_name: str) -> List[Dict[str, Any]]:
    """Extract SEO-relevant content from HTML file."""
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    extracted_data = []
    
    # Extract headings and meta tags
    for tag in ['title', 'meta[name="description"]', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        elements = soup.select(tag)
        for element in elements:
            if tag == 'meta[name="description"]':
                text_value = element.attrs.get('content', '')
            else:
                text_value = element.get_text(strip=True)
            if text_value:
                extracted_data.append({
                    'type': tag.replace('meta[name="description"]', 'meta description'),
                    'value': text_value,
                    'source': source_name
                })
    
    # Extract images
    for img in soup.select('picture img'):
        src = img.get('src')
        alt = img.get('alt')
        
        if src:
            filename = os.path.basename(urlparse(src).path)
            extracted_data.append({
                'type': 'img src',
                'value': filename,
                'source': source_name
            })
        
        if alt:
            extracted_data.append({
                'type': 'img alt',
                'value': alt,
                'source': source_name
            })
    
    # Extract dt/dd tags
    for dt in soup.find_all('dt'):
        text = dt.get_text(strip=True)
        if text:
            extracted_data.append({
                'type': 'dt',
                'value': text,
                'source': source_name
            })
    
    for dd in soup.find_all('dd'):
        text = dd.get_text(strip=True)
        if text:
            extracted_data.append({
                'type': 'dd',
                'value': text,
                'source': source_name
            })
    
    return extracted_data


def process_data_and_visualize(client_url: str, competitor_url: str, queries: List[str], output_dir: str = 'outputs'):
    """Main analysis function."""
    
    # Step 1: Scrape URLs
    print("🔍 Step 1: Scraping URLs...")
    client_html = scrape_url(client_url, "client", output_dir)
    competitor_html = scrape_url(competitor_url, "competitor", output_dir)
    
    # Step 2: Extract content
    print("📄 Step 2: Extracting content...")
    client_data = extract_html_content(client_html, "client")
    competitor_data = extract_html_content(competitor_html, "competitor")
    
    # Combine data
    json_data = {
        client_html: client_data,
        competitor_html: competitor_data
    }
    
    # Step 3: Load embedding model
    print("🧠 Step 3: Loading embedding model...")
    with Halo(text="Loading SentenceTransformer model", spinner="dots") as spinner:
        model = SentenceTransformer('all-MiniLM-L6-v2')
        spinner.succeed("Model loaded")
    
    # Step 4: Generate embeddings
    print("🔢 Step 4: Generating embeddings...")
    
    # Process content embeddings
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
    
    embeddings_data = []
    top_level_embeddings = {}
    
    for url_key, elements in json_data.items():
        element_embeddings = []
        for element in elements:
            embedding = model.encode(element["value"])
            embeddings_data.append({
                'embedding': embedding,
                'label': url_key,
                'type': element["type"],
                'value': element["value"],
                'symbol': symbol_mapping[element["source"]],
                'size': size_mapping[element["source"]]
            })
            element_embeddings.append(embedding)
        top_level_embeddings[url_key] = np.mean(element_embeddings, axis=0)
    
    # Process query embeddings
    with Halo(text="Generating query embeddings", spinner="dots") as spinner:
        query_embeddings = model.encode(queries)
        query_embeddings_data = [
            {
                'embedding': embedding,
                'label': f'Query {i+1}',
                'type': 'Query',
                'value': queries[i],
                'symbol': "x",
                'size': 6
            } for i, embedding in enumerate(query_embeddings)
        ]
        queries_mean = np.mean(query_embeddings, axis=0)
        spinner.succeed("Query embeddings generated")
    
    # Step 5: Reduce dimensions
    print("📊 Step 5: Creating 3D visualization...")
    with Halo(text="Reducing dimensions with t-SNE", spinner="dots") as spinner:
        all_embeddings = np.array([data['embedding'] for data in embeddings_data + query_embeddings_data])
        tsne = TSNE(n_components=3, perplexity=30, random_state=42)
        reduced_embeddings = tsne.fit(all_embeddings)
        spinner.succeed("Dimension reduction completed")
    
    # Add coordinates to data
    for i, data in enumerate(embeddings_data + query_embeddings_data):
        data['x'], data['y'], data['z'] = reduced_embeddings[i]
    
    # Step 6: Calculate similarities
    cosine_similarities = {
        key: cosine_similarity([mean], [queries_mean])[0][0] 
        for key, mean in top_level_embeddings.items()
    }
    
    # Step 7: Create visualization
    df = pd.DataFrame(embeddings_data + query_embeddings_data)
    
    # Create 3D scatter plot
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
        title="Content Embedding Analysis: Client vs Competitor vs Queries"
    )
    
    # Add mean embedding points and arrows
    for key, mean in top_level_embeddings.items():
        # Add mean point
        fig.add_trace(
            go.Scatter3d(
                x=[mean[0]], y=[mean[1]], z=[mean[2]],
                mode='markers',
                marker=dict(size=15, symbol='diamond', color='red'),
                name=f'Mean: {key}',
                showlegend=True
            )
        )
        
        # Add arrow to queries mean
        fig.add_trace(
            go.Scatter3d(
                x=[mean[0], queries_mean[0]],
                y=[mean[1], queries_mean[1]],
                z=[mean[2], queries_mean[2]],
                mode='lines+markers',
                line=dict(color='red', width=3, dash='dot'),
                marker=dict(size=2),
                name=f'{key} → Queries',
                showlegend=True
            )
        )
    
    # Add queries mean point
    fig.add_trace(
        go.Scatter3d(
            x=[queries_mean[0]], y=[queries_mean[1]], z=[queries_mean[2]],
            mode='markers',
            marker=dict(size=15, symbol='star', color='green'),
            name='Queries Mean',
            showlegend=True
        )
    )
    
    # Step 8: Save visualization
    version = 1
    output_file = f"{output_dir}/embedding_comparison-v{version}.html"
    while os.path.exists(output_file):
        version += 1
        output_file = f"{output_dir}/embedding_comparison-v{version}.html"
    
    fig.write_html(output_file)
    print(f"✅ Analysis complete! Visualization saved to: {output_file}")
    
    # Print similarity scores
    print("\n📈 Similarity Scores (higher is better):")
    for key, score in cosine_similarities.items():
        print(f"  {key}: {score:.3f}")
    
    return output_file


def main():
    parser = argparse.ArgumentParser(description="Quick Content Embedding Analysis")
    parser.add_argument("--client", required=True, help="Client URL")
    parser.add_argument("--competitor", required=True, help="Competitor URL")
    parser.add_argument("--queries", required=True, help="Comma-separated list of queries")
    parser.add_argument("--output-dir", default="outputs", help="Output directory")
    
    args = parser.parse_args()
    
    # Parse queries
    queries = [q.strip() for q in args.queries.split(',') if q.strip()]
    
    if not queries:
        print("Error: No valid queries provided")
        sys.exit(1)
    
    print(f"🎯 Analyzing content for:")
    print(f"  Client: {args.client}")
    print(f"  Competitor: {args.competitor}")
    print(f"  Queries: {queries}")
    print(f"  Output: {args.output_dir}")
    print()
    
    try:
        output_file = process_data_and_visualize(
            args.client, 
            args.competitor, 
            queries, 
            args.output_dir
        )
        print(f"\n🚀 Open {output_file} in your browser to view the 3D visualization!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 