import json
import os
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from halo import Halo

# Prompt user for the input JSON file
print("Enter the filename of the input JSON file (e.g., data.json):")
input_file = input("Filename: ").strip()

if not os.path.exists(input_file):
    print(f"Error: The file '{input_file}' does not exist.")
    exit(1)

# Load data from the JSON file
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Handle both dictionary and list structures
# If the JSON is a single dictionary, wrap it in a list for processing
if isinstance(data, dict):
    # Reference: Handles single dictionary JSON structure
    data = [data]

if not isinstance(data, list):
    print("Error: Expected a list of objects in the JSON file.")
    exit(1)

# Debug: Verify JSON data loaded
print(f"Loaded {len(data)} entries from the JSON file.")

# Load embedding model
spinner = Halo(text="Loading SentenceTransformer model", spinner="dots")
spinner.start()
model = SentenceTransformer('sentence-transformers/LaBSE')
spinner.succeed("Model loaded")

# Helper function to calculate similarity
def calculate_similarity(query_embeddings, primary_mean_embedding):
    return cosine_similarity(query_embeddings, primary_mean_embedding.reshape(1, -1)).flatten()

# Process each URL element and output one CSV per URL
for item in data:  # Iterate over the list of dictionaries
    url = item.get("url", "Unknown URL")

    # Prompt user for primary queries for this URL
    print(f"Enter Primary Queries for {url} (separated by commas):")
    input_primary_queries = input("Primary Queries: ").strip()
    primary_queries = [query.strip() for query in input_primary_queries.split(",") if query.strip()]

    # Prompt user for research queries for this URL
    print(f"Enter Research Queries for {url} (separated by commas):")
    input_research_queries = input("Research Queries: ").strip()
    research_queries = [query.strip() for query in input_research_queries.split(",") if query.strip()]

    # Prompt user for GSC queries for this URL
    print(f"Would you like to enter GSC Queries for {url}? (Y/N):")
    include_gsc = input("Include GSC Queries: ").strip().lower()
    if include_gsc == 'y':
        print(f"Enter GSC Queries for {url} (separated by commas):")
        input_gsc_queries = input("GSC Queries: ").strip()
        gsc_queries = [query.strip() for query in input_gsc_queries.split(",") if query.strip()]
    else:
        gsc_queries = []

    # Encode the primary queries and calculate their mean embedding
    primary_embeddings = model.encode(primary_queries)
    primary_mean_embedding = primary_embeddings.mean(axis=0)

    # Encode and calculate similarity for other query types
    research_embeddings = model.encode(research_queries)
    research_similarities = calculate_similarity(research_embeddings, primary_mean_embedding)

    if gsc_queries:
        gsc_embeddings = model.encode(gsc_queries)
        gsc_similarities = calculate_similarity(gsc_embeddings, primary_mean_embedding)
    else:
        gsc_similarities = []

    # Process elements of the current URL
    url_elements = []
    for element in item.get("data", []):
        element_text = element.get("text", "")
        element_tag = element.get("tag", "")
        element_embedding = model.encode([element_text])[0]
        similarity = cosine_similarity([element_embedding], [primary_mean_embedding])[0][0]
        url_elements.append({
            'url': url,
            'element_text': element_text,
            'tag': element_tag,
            'similarity': similarity
        })

    # Output recommendations for the current URL
    recommendations = []
    for element in url_elements:
        for i, query in enumerate(research_queries):
            if research_similarities[i] > element['similarity']:
                recommendations.append({
                    'url': element['url'],
                    'current_text': element['element_text'],
                    'tag': element['tag'],
                    'suggested_query': query,
                    'similarity_gain': research_similarities[i] - element['similarity'],
                    'query_type': 'Research Query'
                })
        if gsc_queries:
            for i, query in enumerate(gsc_queries):
                if gsc_similarities[i] > element['similarity']:
                    recommendations.append({
                        'url': element['url'],
                        'current_text': element['element_text'],
                        'tag': element['tag'],
                        'suggested_query': query,
                        'similarity_gain': gsc_similarities[i] - element['similarity'],
                        'query_type': 'GSC Query'
                    })

    # Convert recommendations to a DataFrame for easier visualization
    recommendations_df = pd.DataFrame(recommendations)

    # Sort recommendations by similarity gain in descending order
    recommendations_df = recommendations_df.sort_values(by="similarity_gain", ascending=False)

    # Generate a unique filename based on the URL
    url_path = url.split(".com/")[-1].replace("/", "_").replace("-", "_")
    output_file = f"{url_path}_scraped_data.csv"
    version = 1
    while os.path.exists(output_file):
        version += 1
        output_file = f"{url_path}_scraped_data_v{version}.csv"

    # Save the recommendations to a CSV file
    recommendations_df.to_csv(output_file, index=False)

    print(f"CSV file generated for {url}: {output_file}")

print("All CSV files have been generated for each URL in the JSON file.")
