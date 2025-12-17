import os
import json
import urllib.request
import urllib.parse
import ssl
import time
import glob

# Path to the Minerobo data
REPO_DATA_PATH = "data/categories"
OUTPUT_FILE = "data/rocks_data.json"

# Wikipedia API setup
# Updated API URL to ensure we get a larger thumbnail image if original is missing/weird
# 'pithumbsize' requests a thumbnail of this width (e.g., 500px)
WIKI_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{}?redirect=true"

# SSL Context
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

rocks_data = []
rock_id_counter = 1

print(f"Reading data from {REPO_DATA_PATH}...")

# Get all .txt files
txt_files = glob.glob(os.path.join(REPO_DATA_PATH, "*.txt"))

for file_path in txt_files:
    filename = os.path.basename(file_path)
    category_name = filename.replace(".txt", "").title()
    
    print(f"Processing Category: {category_name}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        mineral_name = line.strip()
        if not mineral_name:
            continue
            
        mineral_name = mineral_name.title()
        
        # Manual Alias Map for Wikipedia Lookup
        ALIAS_MAP = {
            "Dolomite": "Dolomite (mineral)",
            "Anthracite,Anthracite Coal": "Anthracite",
            "Bituminous Coal,Bituminous": "Bituminous coal",
            "Orthoclase,Potassium Feldspar,Feldspar": "Orthoclase",
            "Apatite,Apatite Group": "Apatite",
            "Citrine": "Citrine (quartz)",
            "Chert,Flint": "Chert",
            "Conglomerate": "Conglomerate (geology)",
            "Rock Salt,Halite": "Halite",
            "Rock Gypsum,Gypsum": "Gypsum",
            "Tourmaline Group,Tourmaline": "Tourmaline",
            "Celestite,Celestine": "Celestine (mineral)",
            "Lignite": "Lignite",
            "Albite": "Albite",
             # Adding known missing ones from previous run just in case
            "Garnet Schist": "Schist", 
            "Mica Schist": "Schist",
        }
        
        lookup_name = ALIAS_MAP.get(mineral_name, mineral_name.split(',')[0].strip())
        
        image_url = ""
        description = ""
        wiki_url = ""
        
        try:
            query = urllib.parse.quote(lookup_name)
            url = WIKI_API_URL.format(query)
            
            req = urllib.request.Request(url, headers={'User-Agent': 'MineroboStaticSiteGenerator/1.0 (https://github.com/Slooquie/SciOlyBugWeb)'})
            with urllib.request.urlopen(req, context=ctx) as response:
                data = json.loads(response.read().decode())
                
                # PREFER ORIGINAL IMAGE
                if 'originalimage' in data:
                    image_url = data['originalimage'].get('source', '')
                elif 'thumbnail' in data:
                    # If only thumbnail exists, it might be tiny.
                    # We can try to modify the URL to get a larger version
                    # e.g. .../50px-Image.jpg -> .../500px-Image.jpg
                    thumb_source = data['thumbnail'].get('source', '')
                    if "px-" in thumb_source:
                         # Hacky way to upscale thumbnail request if API gave us a small one
                         image_url = thumb_source.replace("50px-", "800px-").replace("100px-", "800px-")
                    else:
                        image_url = thumb_source
                
                if 'extract' in data:
                    description = data['extract']
                    if len(description) > 200:
                        description = description.split('.')[0] + '.'
                
                if 'content_urls' in data and 'desktop' in data['content_urls']:
                    wiki_url = data['content_urls']['desktop']['page']
                    
        except Exception as e:
            print(f"  Error fetching {mineral_name}: {e}")
            
        entry = {
            "id": str(rock_id_counter),
            "common_name": mineral_name,
            "scientific_name": mineral_name,
            "category": category_name,
            "image_url": image_url,
            "source_url": wiki_url,
            "key_facts": description
        }
        
        if image_url:
            rocks_data.append(entry)
            rock_id_counter += 1
            print(f"  + Added: {mineral_name}")
        else:
            print(f"  - Skipped (no image): {mineral_name}")
            
        time.sleep(0.1) 

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(rocks_data, f, indent=4)

print(f"\nSuccessfully generated {OUTPUT_FILE} with {len(rocks_data)} entries.")
