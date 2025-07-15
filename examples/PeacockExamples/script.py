import json
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

# Load data from JSON files
original_json_file = "original_extracted_html_data.json"
updated_json_file = "update_extracted_html_data.json"

with open(original_json_file, "r", encoding="utf-8") as f:
    original_data = json.load(f)

with open(updated_json_file, "r", encoding="utf-8") as f:
    updated_data = json.load(f)

# Prompt user for queries
input_queries = input("Enter up to 20 queries, separated by commas: ")
queries = [query.strip() for query in input_queries.split(",") if query.strip()]

if len(queries) > 20:
    print("Error: You entered more than 20 queries. Please try again.")
    exit(1)

print(f"Using the following queries:\n{queries}")

# Queries for embeddings
# queries = [
#     "temporary storage for luggage in milan",
#     "affordable luggage lockers in milan",
#     "best luggage storage options in milan",
#     "milan luggage storage near vatican",
#     "milan travel bag storage services",
#     "where to store luggage near milan train station",
#     "secure luggage storage milan city center",
#     "bag storage in milan",
#     "overnight bag storage milan",
#     "luggage storage milan",
#     "milan baggage storage locations"
# ]

# Load embedding model
spinner = Halo(text="Loading SentenceTransformer model", spinner="dots")
spinner.start()
model = SentenceTransformer('all-MiniLM-L6-v2')
spinner.succeed("Model loaded")

# Helper function to process JSON data
def process_json_data(json_data, symbol_mapping, size_mapping):
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
        # Compute mean embedding for each top-level key
        top_level_embeddings[url_key] = np.mean(element_embeddings, axis=0)
    return embeddings_data, top_level_embeddings

# Symbol and size mappings
symbol_mapping = {
    "Bounce.com - Main": "circle",
    "Bounce.com - Other": "diamond",
    "Competitor": "square",
    "Query": "x"
}

size_mapping = {
    "Bounce.com - Main": 10,
    "Bounce.com - Other": 5,
    "Competitor": 8,
    "Query": 6
}

# Process original and updated JSON data
spinner = Halo(text="Processing original JSON data", spinner="dots")
spinner.start()
original_embeddings_data, original_means = process_json_data(original_data, symbol_mapping, size_mapping)
spinner.succeed("Original JSON data processed")

spinner = Halo(text="Processing updated JSON data", spinner="dots")
spinner.start()
updated_embeddings_data, updated_means = process_json_data(updated_data, symbol_mapping, size_mapping)
spinner.succeed("Updated JSON data processed")

# Process query embeddings
spinner = Halo(text="Generating query embeddings", spinner="dots")
spinner.start()
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

original_df = reduce_dimensions(original_embeddings_data + query_embeddings_data)
updated_df = reduce_dimensions(updated_embeddings_data + query_embeddings_data)

# Calculate cosine similarities
cosine_similarities = {
    "original": {key: cosine_similarity([mean], [queries_mean])[0][0] for key, mean in original_means.items()},
    "updated": {key: cosine_similarity([mean], [queries_mean])[0][0] for key, mean in updated_means.items()}
}

# Combine all visuals into one HTML file
def create_combined_html():
    # Original JSON Visualization
    original_fig = px.scatter_3d(
        original_df,
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
        title="Original JSON Visualization"
    )

    # Updated JSON Visualization
    updated_fig = px.scatter_3d(
        updated_df,
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
        title="Updated JSON Visualization"
    )

    # Mean Embeddings Visualization with Arrows
    mean_embeddings_data = [
        {'label': f'Original Mean: {key}', 'x': original_means[key][0], 'y': original_means[key][1], 'z': original_means[key][2], 'symbol': 'circle', 'size': 12}
        for key in original_means
    ] + [
        {'label': f'Updated Mean: {key}', 'x': updated_means[key][0], 'y': updated_means[key][1], 'z': updated_means[key][2], 'symbol': 'diamond', 'size': 12}
        for key in updated_means
    ] + [
        {'label': 'Queries Mean', 'x': queries_mean[0], 'y': queries_mean[1], 'z': queries_mean[2], 'symbol': 'x', 'size': 12}
    ]

    mean_df = pd.DataFrame(mean_embeddings_data)
    scatter = px.scatter_3d(
        mean_df,
        x='x', y='y', z='z',
        color='label',
        symbol='symbol',
        size='size',
        title="Mean Embeddings Visualization with Arrows"
    )

    # Add arrows from Original to Updated and to Queries Mean
    for key in original_means.keys():
        scatter.add_trace(
            go.Scatter3d(
                x=[original_means[key][0], updated_means[key][0]],
                y=[original_means[key][1], updated_means[key][1]],
                z=[original_means[key][2], updated_means[key][2]],
                mode='lines+markers',
                line=dict(color='blue', width=2, dash='dot'),
                marker=dict(size=2),
                name=f"{key}: Original to Updated"
            )
        )
        scatter.add_trace(
            go.Scatter3d(
                x=[original_means[key][0], queries_mean[0]],
                y=[original_means[key][1], queries_mean[1]],
                z=[original_means[key][2], queries_mean[2]],
                mode='lines+markers',
                line=dict(color='red', width=2),
                marker=dict(size=2),
                name=f"{key}: Original to Queries"
            )
        )
        scatter.add_trace(
            go.Scatter3d(
                x=[updated_means[key][0], queries_mean[0]],
                y=[updated_means[key][1], queries_mean[1]],
                z=[updated_means[key][2], queries_mean[2]],
                mode='lines+markers',
                line=dict(color='green', width=2),
                marker=dict(size=2),
                name=f"{key}: Updated to Queries"
            )
        )

    # Cosine Similarities Scatter Plot
    similarity_data = [
        {'Key': key, 'Cosine Similarity': value, 'Type': 'Original'}
        for key, value in cosine_similarities["original"].items()
    ] + [
        {'Key': key, 'Cosine Similarity': value, 'Type': 'Updated'}
        for key, value in cosine_similarities["updated"].items()
    ]
    similarity_df = pd.DataFrame(similarity_data)
    cosine_fig = px.scatter(
        similarity_df,
        x='Key',
        y='Cosine Similarity',
        color='Type',
        title="Cosine Similarities for Original and Updated Mean Embeddings"
    )

    # Combine all visuals into one HTML file
    combined_html = f"""
    <html>
    <head>
        <title>Combined Plotly Visualizations</title>
    </head>
    <body>
        <h1>Original JSON Visualization</h1>
        {pio.to_html(original_fig, full_html=False)}
        <h1>Updated JSON Visualization</h1>
        {pio.to_html(updated_fig, full_html=False)}
        <h1>Mean Embeddings Visualization with Arrows</h1>
        {pio.to_html(scatter, full_html=False)}
        <h1>Cosine Similarities</h1>
        {pio.to_html(cosine_fig, full_html=False)}
    </body>
    </html>
    """

    with open("combined_visualizations.html", "w", encoding="utf-8") as f:
        f.write(combined_html)
    print("Combined visualizations saved as combined_visualizations.html")

# Generate combined HTML
create_combined_html()
