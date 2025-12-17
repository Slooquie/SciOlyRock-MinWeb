import os
import json
import urllib.request
import urllib.parse
import ssl
import time
import glob
import shutil
import subprocess

# Configuration
OUTPUT_FILE = "data/rocks_data.json"
TEMP_REPO_DIR = "temp_minerobo_source"
REPO_URL = "https://github.com/tctree333/Minerobo.git"
WIKI_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{}?redirect=true"

# SSL Context
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

rocks_data = []
rock_id_counter = 1

def fetch_data():
    global rock_id_counter
    
    # 1. Clone the repo to get the list
    if os.path.exists(TEMP_REPO_DIR):
        shutil.rmtree(TEMP_REPO_DIR)
        
    print(f"Cloning source repository ({REPO_URL})...")
    try:
        subprocess.run(["git", "clone", REPO_URL, TEMP_REPO_DIR], check=True)
    except Exception as e:
        print(f"Error cloning repo: {e}")
        return

    # 2. Read files
    repo_data_path = os.path.join(TEMP_REPO_DIR, "data", "categories")
    txt_files = glob.glob(os.path.join(repo_data_path, "*.txt"))
    
    print(f"Found {len(txt_files)} category files. Processing...")

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
                "Garnet Schist": "Schist", 
                "Mica Schist": "Schist",
                "Fossiliferous Limestone,Fossiliferous,Fossil Limestone": "Fossiliferous limestone",
                "Oolitic Limestone,Oolitic,Oolite": "Oolite",
                "Quartz Sandstone": "Sandstone",
                "Rock Crystal,Crystal": "Rock crystal",
                "Soapstone,Talc Schist": "Soapstone",
                "Banded Iron,Banded Iron Formation,Bif": "Banded iron formation"
            }
            
            lookup_name = ALIAS_MAP.get(mineral_name, mineral_name.split(',')[0].strip())
            
            image_url = ""
            description = ""
            wiki_url = ""
            
            try:
                query = urllib.parse.quote(lookup_name)
                url = WIKI_API_URL.format(query)
                
                req = urllib.request.Request(url, headers={'User-Agent': 'MineroboStaticSiteGenerator/1.0'})
                with urllib.request.urlopen(req, context=ctx) as response:
                    data = json.loads(response.read().decode())
                    
                    # PRIORITY: Original Image > Large Thumbnail > Standard Thumbnail
                    if 'originalimage' in data:
                        image_url = data['originalimage'].get('source', '')
                    elif 'thumbnail' in data:
                        thumb_source = data['thumbnail'].get('source', '')
                        # Try to request a larger thumbnail (e.g. 800px) by hacking the URL
                        # Wikipedia thumb URLs are like: .../50px-Filename.jpg
                        # We change 50px- to 800px-
                        if "px-" in thumb_source:
                            import re
                            image_url = re.sub(r'\d+px-', '800px-', thumb_source)
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

    # 3. Cleanup
    print("Cleaning up temp files...")
    if os.path.exists(TEMP_REPO_DIR):
        shutil.rmtree(TEMP_REPO_DIR)

    # 4. Save
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(rocks_data, f, indent=4)

    print(f"\nSuccessfully generated {OUTPUT_FILE} with {len(rocks_data)} High-Res entries.")

if __name__ == "__main__":
    fetch_data()
