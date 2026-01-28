import requests
import zipfile
import shutil
import os
from tqdm import tqdm

def download_file(url, filename):
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024 # 1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    with open(filename, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()

def download_hf_dataset():
    url = "https://deepblue.lib.umich.edu/data/downloads/rr171x63c"
    local_dir = os.path.join("repo", "data", "pills_inside_bottles")
    zip_path = os.path.join(local_dir, "dataset.zip")
    
    os.makedirs(local_dir, exist_ok=True)
    
    print(f"Downloading dataset from {url}...")
    try:
        download_file(url, zip_path)
        print("Download complete. Extracting...")
        
        shutil.unpack_archive(zip_path, local_dir)
        print(f"Extracted to {local_dir}")
        
        # Cleanup zip to save space
        os.remove(zip_path)
        print("Cleanup complete.")
        
    except Exception as e:
        print(f"Error downloading or extracting: {e}")

if __name__ == "__main__":
    download_hf_dataset()
