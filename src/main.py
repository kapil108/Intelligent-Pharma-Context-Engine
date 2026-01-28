import os
import json
import sys
import glob

# Ensure imports work from current directory
sys.path.append(os.path.dirname(__file__))

from vision import ImagePreprocessor
from extraction import Extractor
from context import PharmaBrain

# --- CONFIGURATION (Adapted to repo structure) ---
REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
TEST_IMAGE_DIR = os.path.join(REPO_ROOT, "data", "sample") # Uses the sample folder we created
RXNORM_PATH = os.path.join(REPO_ROOT, "data", "rxnorm_local.csv")
OPENFDA_DIR = os.path.join(REPO_ROOT, "data", "openfda_labels")
OUTPUT_FILE = os.path.join(REPO_ROOT, "results", "final_output.json")

def main():
    # 1. Initialize Modules
    print("[*] Initializing Engine Modules...")
    preprocessor = ImagePreprocessor()
    extractor = Extractor()
    brain = PharmaBrain(rxnorm_path=RXNORM_PATH, openfda_dir=OPENFDA_DIR)

    results = []

    # 2. Processing Loop
    print(f"[*] Scanning images in {TEST_IMAGE_DIR}...")
    valid_images = glob.glob(os.path.join(TEST_IMAGE_DIR, "*"))
    valid_images = [f for f in valid_images if f.lower().endswith(('.jpg', '.png', '.jpeg'))]

    if not valid_images:
        print(f"No images found in {TEST_IMAGE_DIR}. Please add images to test.")
        return

    for img_path in valid_images:
        img_name = os.path.basename(img_path)
        print(f"\nProcessing: {img_name}")

        try:
            # Step A: Vision (Clean the image)
            clean_img = preprocessor.process(img_path)

            # Step B: Extraction (Get Barcode & Text)
            barcode = extractor.get_barcode(clean_img)
            raw_text = extractor.get_text(clean_img)
            
            print(f"   -> OCR Found: {raw_text[:3]}... (truncated)")
            if barcode:
                print(f"   -> Barcode Found: {barcode}")

            # Step C: Intelligence (Verify & Enrich)
            drug_name, confidence = brain.fuzzy_match_drug(raw_text)
            
            enrichment_data = {}
            if drug_name:
                print(f"   -> VERIFIED DRUG: {drug_name} (Confidence: {confidence}%)")
                enrichment_data = brain.get_enrichment(drug_name)
            else:
                print("   -> No valid drug name found.")

            # Step D: Structuring Output
            record = {
                "file": img_name,
                "raw_ocr": raw_text,
                "barcode": barcode,
                "verified_drug": drug_name,
                "confidence_score": confidence,
                "clinical_data": enrichment_data
            }
            results.append(record)

        except Exception as e:
            print(f"   [!] Error processing {img_name}: {e}")
            with open("error.log", "a") as err_log:
                import traceback
                err_log.write(f"Error processing {img_name}:\n")
                traceback.print_exc(file=err_log)
                err_log.write("\n")

    # 3. Save Results
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=4)
    print(f"\n[*] Success! Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
