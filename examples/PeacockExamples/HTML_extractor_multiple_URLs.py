import requests
from bs4 import BeautifulSoup
import json
import os

# Function to extract specific HTML elements
def extract_html_values(url):
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
                        'tag': tag,
                        'text': text_value
                    })
        return {'url': url, 'data': extracted_data}
    except requests.RequestException as e:
        return {'url': url, 'error': str(e)}

# Function to generate a unique output filename
def get_unique_filename(base_name):
    version = 1
    while os.path.exists(f"{base_name}_{version}.json"):
        version += 1
    return f"{base_name}_{version}.json"

# Main function to process multiple URLs
def process_urls(urls, output_base_name):
    results = []
    for url in urls:
        print(f"Processing URL: {url}")
        results.append(extract_html_values(url))

    output_filename = get_unique_filename(output_base_name)
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        json.dump(results, outfile, indent=4, ensure_ascii=False)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    # Prompt user to enter URLs
    user_input = input("Enter URLs separated by commas: ")
    urls = [url.strip() for url in user_input.split(',') if url.strip()]

    # File to save results
    output_base_name = "scraped_data"

    # Process the URLs
    process_urls(urls, output_base_name)
