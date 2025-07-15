from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urlparse


def extract_html_values(filepath, source_name):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')

    extracted_data = []

    # Headings and meta
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

    # Images inside <picture> tags
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

    # <dt> and <dd> tags
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

# Prompt user for local HTML files
input_files = {
    "Primary HTML file": "wicked_peacock.html",
    "Competitor HTML file": "wicked_apple.html"
}

output_data = {}
for label, filename in input_files.items():
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        continue
    print(f"Extracting from {filename}...")
    output_data[filename] = extract_html_values(filename, label)

# Save unified output
base_name = "extracted_html_data"
version = 1
output_file = f"{base_name}.json"

while os.path.exists(output_file):
    version += 1
    output_file = f"{base_name}-v{version}.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=4, ensure_ascii=False)

print(f"Saved {output_file}")
