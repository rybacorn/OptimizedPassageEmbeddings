import json
import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from openTSNE import TSNE
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from sklearn.metrics.pairwise import cosine_similarity
from halo import Halo
import plotly.io as pio

# Prompt user for the JSON file to use
print("Enter the filename of the input JSON file (e.g., data.json):")
input_file = input("Filename: ").strip()

if not os.path.exists(input_file):
    print(f"Error: The file '{input_file}' does not exist.")
    exit(1)

# Load data from the JSON file
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Prompt user for queries
input_queries = input("Enter up to 20 queries, separated by commas: ")
queries = [query.strip() for query in input_queries.split(",") if query.strip()]

if len(queries) > 20:
    print("Error: You entered more than 20 queries. Please try again.")
    exit(1)

print(f"Using the following queries:\n{queries}")

# Load embedding model
spinner = Halo(text="Loading SentenceTransformer model", spinner="dots")
spinner.start()
model = SentenceTransformer('all-MiniLM-L6-v2')
spinner.succeed("Model loaded")

# Helper function to process JSON data
def process_json_data(json_data):
    embeddings_data = []
    for i, item in enumerate(json_data):
        url = item["url"]
        elements = item["data"]
        for element in elements:
            embedding = model.encode(element["text"])
            embeddings_data.append({
                'embedding': embedding,
                'label': url,
                'type': element["tag"],
                'value': element["text"],
                'symbol': "circle",
                'size': 10 if i == 0 else 5  # First URL size 10, others size 5
            })
    return embeddings_data

# Process JSON data
spinner = Halo(text="Processing JSON data", spinner="dots")
spinner.start()
embeddings_data = process_json_data(data)
spinner.succeed("JSON data processed")

# Generate query embeddings
spinner = Halo(text="Generating query embeddings", spinner="dots")
spinner.start()
query_embeddings = model.encode(queries)
query_embeddings_data = [
    {
        'embedding': embedding,
        'label': 'Queries',
        'type': 'Query',
        'value': queries[i],
        'symbol': "x",  # Explicitly use "x" for queries
        'size': 10  # Increased size for better visibility
    } for i, embedding in enumerate(query_embeddings)
]
spinner.succeed("Query embeddings generated")

# Combine embeddings and reduce dimensions
def reduce_dimensions(embeddings_data):
    spinner = Halo(text="Reducing dimensions with t-SNE", spinner="dots")
    spinner.start()
    all_embeddings = np.array([data['embedding'] for data in embeddings_data])
    tsne = TSNE(n_components=3, perplexity=30, random_state=42)
    reduced_embeddings = tsne.fit(all_embeddings)
    spinner.succeed("Dimension reduction completed")
    for i, data in enumerate(embeddings_data):
        data['x'], data['y'], data['z'] = reduced_embeddings[i]
    return pd.DataFrame(embeddings_data)

reduced_df = reduce_dimensions(embeddings_data + query_embeddings_data)

# Generate HTML file
def create_html_output():
    version = 1
    output_file = "visualizations.html"

    while os.path.exists(output_file):
        version += 1
        output_file = f"visualizations-v{version}.html"

    # Generate visualization
    fig = px.scatter_3d(
        reduced_df,
        x='x', y='y', z='z',
        color='label',
        symbol='symbol',
        size='size',
        symbol_sequence=["circle", "x"],  # Explicitly define symbol sequence
        hover_data={
            'type': True,
            'value': True,
            'label': False,
            'symbol': False,
            'size': False
        },
        title="3D Embedding Visualization"
    )

    html_content = pio.to_html(fig, full_html=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Visualization saved to {output_file}")

create_html_output()
