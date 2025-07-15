import json
import os
from halo import Halo

# Ask for input filename
input_file = input("Enter the name of the extracted JSON file: ").strip()

if not os.path.exists(input_file):
    print(f"Error: File '{input_file}' not found.")
    exit(1)

spinner = Halo(text=f"Loading {input_file}", spinner="dots")
spinner.start()
with open(input_file, "r", encoding="utf-8") as f:
    raw = json.load(f)
spinner.succeed("Loaded extracted HTML data")

spinner = Halo(text="Reformatting data for scriptCity.py", spinner="dots")
spinner.start()
formatted = []
for url_key, elements in raw.items():
    block = {
        "url": url_key,
        "data": [
            {"tag": el["type"], "text": el["value"]}
            for el in elements
        ]
    }
    formatted.append(block)
spinner.succeed("Reformatting complete")

# Versioned output filename
base_name = "reformatted_input"
version = 1
output_file = f"{base_name}.json"
while os.path.exists(output_file):
    version += 1
    output_file = f"{base_name}-v{version}.json"

spinner = Halo(text=f"Saving {output_file}", spinner="dots")
spinner.start()
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(formatted, f, indent=4, ensure_ascii=False)
spinner.succeed(f"Saved as {output_file}")
