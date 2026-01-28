import os
import json
import zipfile
import requests
import sqlite3
from tqdm import tqdm

FDA_DOWNLOAD_URL = "https://download.open.fda.gov/drug/label/drug-label-0001-of-0001.json.zip"
DATA_DIR = os.path.join("repo", "data", "openfda_labels")
ZIP_PATH = os.path.join(DATA_DIR, "drug-label-0001-of-0001.json.zip")
DB_PATH = os.path.join(DATA_DIR, "fda_labels.db")

def download_fda_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(ZIP_PATH):
        print("FDA data already downloaded.")
        return

    print("Fetching valid download URL from openFDA API...")
    try:
        # Get the index of all downloads
        index_response = requests.get("https://api.fda.gov/download.json")
        index_data = index_response.json()
        
        # Navigate to Drug -> Label -> Part 1
        # Structure: results -> drug -> label -> partitions -> [0] -> file
        # Note: This is an assumption of structure, needs safety checks
        drug_labels = index_data['results']['drug']['label']['partitions']
        #Sort to get the first one usually or just take the first
        download_url = drug_labels[0]['file']
        print(f"Found download URL: {download_url}")
        
    except Exception as e:
        print(f"Error fetching dynamic URL: {e}")
        # Fallback (though likely to fail if dynamic failed)
        download_url = "https://download.open.fda.gov/drug/label/drug-label-0001-of-0011.json.zip"

    print(f"Downloading openFDA bulk data from {download_url}...")
    try:
        response = requests.get(download_url, stream=True)
        if response.status_code != 200:
            print(f"Failed to download FDA data. Status code: {response.status_code}")
            return
        total_size = int(response.headers.get('content-length', 0))
    except Exception as e:
        print(f"Error downloading FDA data: {e}")
        return
    
    with open(ZIP_PATH, "wb") as f, tqdm(
        desc="Downloading",
        total=total_size,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = f.write(data)
            bar.update(size)

def index_fda_data():
    if os.path.exists(DB_PATH):
        print("FDA database already indexed.")
        return

    print("Unzipping and indexing FDA data into SQLite...")
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        json_filename = zip_ref.namelist()[0]
        with zip_ref.open(json_filename) as f:
            data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE labels (
            id TEXT PRIMARY KEY,
            brand_name TEXT,
            generic_name TEXT,
            manufacturer_name TEXT,
            dosage_form TEXT,
            storage_instructions TEXT,
            side_effects TEXT,
            warnings TEXT,
            raw_json TEXT
        )
    ''')

    for record in tqdm(data.get('results', []), desc="Indexing"):
        openfda = record.get('openfda', {})
        brand_name = openfda.get('brand_name', [None])[0]
        generic_name = openfda.get('generic_name', [None])[0]
        manufacturer_name = openfda.get('manufacturer_name', [None])[0]
        
        # Some fields might be in large text blocks
        dosage_form = record.get('dosage_and_administration', [None])[0]
        storage_instructions = record.get('how_supplied', [None])[0]
        side_effects = record.get('adverse_reactions', [None])[0]
        warnings = record.get('warnings', [None])[0]

        cursor.execute('''
            INSERT OR REPLACE INTO labels 
            (id, brand_name, generic_name, manufacturer_name, dosage_form, storage_instructions, side_effects, warnings, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.get('id'),
            brand_name,
            generic_name,
            manufacturer_name,
            dosage_form,
            storage_instructions,
            side_effects,
            warnings,
            json.dumps(record)
        ))

    conn.commit()
    conn.close()
    print(f"Indexed FDA data to {DB_PATH}")

if __name__ == "__main__":
    download_fda_data()
    index_fda_data()
