import os
import sys
import json
import cv2

# Ensure we can import from src
# sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from src.pipeline import PharmaPipeline

def verify_upload():
    print("Initializing Pipeline...")
    pipeline = PharmaPipeline()
    
    # Path to the specific uploaded image (from user metadata)
    # The path provided in metadata was: C:/Users/kapil/.gemini/antigravity/brain/061f6500-0ec4-414a-9ce9-f0e4843372f6/uploaded_media_1769614707319.png
    # formatting for python string:
    image_path = r"C:/Users/kapil/.gemini/antigravity/brain/061f6500-0ec4-414a-9ce9-f0e4843372f6/uploaded_media_1769614707319.png"
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        # Fallback to checking the temp file app.py creates if possible, or just fail
        return

    print(f"Processing image: {image_path}")
    try:
        result = pipeline.process_image(image_path)
        
        output_str = ""
        output_str += "\n" + "="*40 + "\n"
        output_str += "          VERIFICATION RESULT\n"
        output_str += "="*40 + "\n"
        
        fields = result['fields']
        output_str += f"Detected Drug Name: {fields['drug_name']['value']}\n"
        output_str += f"Confidence:         {fields['drug_name']['confidence']*100:.2f}%\n"
        
        output_str += "-" * 20 + "\n"
        barcode_val = fields['barcode']['value']
        output_str += f"Detected Barcode:   {barcode_val if barcode_val else 'None'}\n"
        
        output_str += "-" * 20 + "\n"
        meta = fields['meta']
        output_str += f"Manufacturer:       {meta.get('manufacturer')}\n"
        output_str += f"Dosage:             {meta.get('dosage')}\n"
        
        output_str += "-" * 20 + "\n"
        verify = result['verification']
        output_str += f"FDA Verified:       {verify['matched_source'] is not None}\n"
        output_str += f"RxNorm CUI:         {verify.get('rxcui')}\n"
        output_str += "="*40 + "\n"

        print(output_str)
        with open("verify_result_final.txt", "w") as f:
            f.write(output_str)

    except Exception as e:
        err_msg = f"\n--- Failure ---\nError: {e}\n"
        print(err_msg)
        import traceback
        traceback.print_exc()
        with open("verify_result_final.txt", "w") as f:
            f.write(err_msg)

if __name__ == "__main__":
    verify_upload()
