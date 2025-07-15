import json
import numpy as np
import plotly.graph_objects as go
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from openTSNE import TSNE
from halo import Halo
import os

# Prompt for input filenames and queries
original_file = input("Enter the original JSON filename: ").strip()
update_file = input("Enter the updated JSON filename: ").strip()
queries_input = input("Enter target queries separated by commas: ").strip()
queries = [q.strip() for q in queries_input.split(',') if q.strip()]

# Spinner for loading JSON
spinner = Halo(text='Loading JSON files', spinner='dots')
spinner.start()
with open(original_file, "r", encoding="utf-8") as f:
    original_data = json.load(f)
with open(update_file, "r", encoding="utf-8") as f:
    update_data = json.load(f)
spinner.succeed("Loaded JSON files")

# Spinner for parsing site-specific data
spinner = Halo(text='Extracting Apple vs Peacock text content', spinner='dots')
spinner.start()

def extract_texts_by_host(data, host_filter):
    return [el['text'] for page in data if host_filter in page['url'] for el in page['data'] if isinstance(el['text'], str) and el['text'].strip()]

original_peacock = extract_texts_by_host(original_data, "peacock")
original_apple = extract_texts_by_host(original_data, "apple")
update_peacock = extract_texts_by_host(update_data, "peacock")
update_apple = extract_texts_by_host(update_data, "apple")
spinner.succeed("Text extracted and categorized")

# Spinner for embedding
spinner = Halo(text='Generating embeddings', spinner='dots')
spinner.start()
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = {
    "original_peacock": model.encode(original_peacock),
    "original_apple": model.encode(original_apple),
    "update_peacock": model.encode(update_peacock),
    "update_apple": model.encode(update_apple),
    "queries": model.encode(queries)
}
spinner.succeed("Embeddings generated")

# Compute mean embeddings
means = {k: np.mean(v, axis=0) for k, v in embeddings.items()}
peacock_cosine = cosine_similarity([means['original_peacock']], [means['update_peacock']])[0][0]
apple_cosine = cosine_similarity([means['original_apple']], [means['update_apple']])[0][0]

# Reduce all points to 3D
spinner = Halo(text='Reducing dimensions with t-SNE', spinner='dots')
spinner.start()
all_vectors = np.vstack([
    embeddings['original_peacock'], embeddings['update_peacock'],
    embeddings['original_apple'], embeddings['update_apple'],
    means['original_peacock'], means['update_peacock'],
    means['original_apple'], means['update_apple'],
    embeddings['queries'], means['queries']
])
reduced = TSNE(n_components=3, perplexity=30, random_state=42).fit(all_vectors)
spinner.succeed("t-SNE reduction complete")

# Index mapping
n_op = len(embeddings['original_peacock'])
n_up = len(embeddings['update_peacock'])
n_oa = len(embeddings['original_apple'])
n_ua = len(embeddings['update_apple'])
n_q = len(embeddings['queries'])
i_mop = n_op + n_up + n_oa + n_ua
i_mup = i_mop + 1
i_moa = i_mop + 2
i_mua = i_mop + 3
i_queries = i_mop + 4

# Plot
fig = go.Figure()
fig.add_trace(go.Scatter3d(x=reduced[:n_op,0], y=reduced[:n_op,1], z=reduced[:n_op,2],
                           mode='markers', marker=dict(size=4, color='blue'), name='Peacock Original', text=original_peacock))
fig.add_trace(go.Scatter3d(x=reduced[n_op:n_op+n_up,0], y=reduced[n_op:n_op+n_up,1], z=reduced[n_op:n_op+n_up,2],
                           mode='markers', marker=dict(size=4, color='green'), name='Peacock Updated', text=update_peacock))
fig.add_trace(go.Scatter3d(x=reduced[n_op+n_up:n_op+n_up+n_oa,0], y=reduced[n_op+n_up:n_op+n_up+n_oa,1], z=reduced[n_op+n_up:n_op+n_up+n_oa,2],
                           mode='markers', marker=dict(size=4, color='red'), name='Apple Original', text=original_apple))
fig.add_trace(go.Scatter3d(x=reduced[n_op+n_up+n_oa:n_op+n_up+n_oa+n_ua,0], y=reduced[n_op+n_up+n_oa:n_op+n_up+n_oa+n_ua,1], z=reduced[n_op+n_up+n_oa:n_op+n_up+n_oa+n_ua,2],
                           mode='markers', marker=dict(size=4, color='orange'), name='Apple Updated', text=update_apple))

# Mean dots
fig.add_trace(go.Scatter3d(x=[reduced[i_mop,0]], y=[reduced[i_mop,1]], z=[reduced[i_mop,2]],
                           mode='markers+text', marker=dict(size=8, color='blue'), name='Mean Peacock Original', text=['Mean Peacock Original']))
fig.add_trace(go.Scatter3d(x=[reduced[i_mup,0]], y=[reduced[i_mup,1]], z=[reduced[i_mup,2]],
                           mode='markers+text', marker=dict(size=8, color='green'), name='Mean Peacock Updated', text=['Mean Peacock Updated']))
fig.add_trace(go.Scatter3d(x=[reduced[i_moa,0]], y=[reduced[i_moa,1]], z=[reduced[i_moa,2]],
                           mode='markers+text', marker=dict(size=8, color='red'), name='Mean Apple Original', text=['Mean Apple Original']))
fig.add_trace(go.Scatter3d(x=[reduced[i_mua,0]], y=[reduced[i_mua,1]], z=[reduced[i_mua,2]],
                           mode='markers+text', marker=dict(size=8, color='orange'), name='Mean Apple Updated', text=['Mean Apple Updated']))
fig.add_trace(go.Scatter3d(x=reduced[i_queries:i_queries+n_q,0], y=reduced[i_queries:i_queries+n_q,1], z=reduced[i_queries:i_queries+n_q,2],
                           mode='markers+text', marker=dict(size=6, color='purple'), name='Queries', text=queries))
fig.add_trace(go.Scatter3d(x=[reduced[i_queries+n_q,0]], y=[reduced[i_queries+n_q,1]], z=[reduced[i_queries+n_q,2]],
                           mode='markers+text', marker=dict(size=10, color='purple'), name='Mean Query', text=['Mean Query']))

# Arrows
fig.add_trace(go.Scatter3d(x=[reduced[i_mop,0], reduced[i_mup,0]], y=[reduced[i_mop,1], reduced[i_mup,1]], z=[reduced[i_mop,2], reduced[i_mup,2]],
                           mode='lines', line=dict(color='black', width=4, dash='dot'), name='Peacock Shift'))
fig.add_trace(go.Scatter3d(x=[reduced[i_moa,0], reduced[i_mua,0]], y=[reduced[i_moa,1], reduced[i_mua,1]], z=[reduced[i_moa,2], reduced[i_mua,2]],
                           mode='lines', line=dict(color='gray', width=4, dash='dot'), name='Apple Shift'))
fig.add_trace(go.Scatter3d(x=[reduced[i_mop,0], reduced[i_queries+n_q,0]], y=[reduced[i_mop,1], reduced[i_queries+n_q,1]], z=[reduced[i_mop,2], reduced[i_queries+n_q,2]],
                           mode='lines', line=dict(color='blue', width=2), name='Peacock Original → Query'))
fig.add_trace(go.Scatter3d(x=[reduced[i_mup,0], reduced[i_queries+n_q,0]], y=[reduced[i_mup,1], reduced[i_queries+n_q,1]], z=[reduced[i_mup,2], reduced[i_queries+n_q,2]],
                           mode='lines', line=dict(color='green', width=2), name='Peacock Updated → Query'))

fig.update_layout(title=(f"Embedding Comparison to Query Mean\n"
                         f"Peacock Mean Cosine Δ: {peacock_cosine:.4f} | Apple Mean Cosine Δ: {apple_cosine:.4f}"),
                  scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))

# Versioned HTML save
base_name = "embedding_comparison"
version = 1
output_file = f"{base_name}.html"
while os.path.exists(output_file):
    version += 1
    output_file = f"{base_name}-v{version}.html"

spinner = Halo(text=f"Saving {output_file}", spinner='dots')
spinner.start()
fig.write_html(output_file)
spinner.succeed(f"Saved {output_file}")
