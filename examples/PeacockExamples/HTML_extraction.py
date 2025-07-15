import requests
from bs4 import BeautifulSoup
import json

# Function to extract specific HTML elements
def extract_html_values(url, source_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract specific HTML elements
        extracted_data = []
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

        return extracted_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL {url}: {e}")
        return []

# Ask user for URLs
primary_url = input("Enter the Primary URL (e.g., Example.com main URL): ")
competitor_url = input("Enter the Competitor URL: ")
secondary_url = input("Enter the Secondary URL for comparison: ")

# Define sources for each URL
urls = {
    "Primary URL": (primary_url, "Example.com - Main"),
    "Competitor URL": (competitor_url, "Competitor"),
    "Secondary URL": (secondary_url, "Example.com - Other")
}

# Extract data from each URL and store in a dictionary
output_data = {}
for key, (url, source_name) in urls.items():
    simplified_url = "/".join(url.split("/")[3:])
    extracted_data = extract_html_values(url, source_name)
    output_data[simplified_url] = extracted_data

# Save data to a JSON file
output_file = "extracted_html_data.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

print(f"Data extracted and saved to {output_file}.")
