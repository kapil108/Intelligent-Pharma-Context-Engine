import os
os.chdir(r"c:/Users/kapil/OneDrive/Desktop/Intelligent Pharma-Context Engine/repo")

from src.pipeline import Pipeline

# Test the 3 new images
test_images = [
    r"C:/Users/kapil/.gemini/antigravity/brain/061f6500-0ec4-414a-9ce9-f0e4843372f6/uploaded_media_0_1769623806938.jpg",
    r"C:/Users/kapil/.gemini/antigravity/brain/061f6500-0ec4-414a-9ce9-f0e4843372f6/uploaded_media_1_1769623806938.jpg",
    r"C:/Users/kapil/.gemini/antigravity/brain/061f6500-0ec4-414a-9ce9-f0e4843372f6/uploaded_media_2_1769623806938.jpg"
]

pipeline = Pipeline()

for i, img_path in enumerate(test_images, 1):
    print(f"\n{'='*50}")
    print(f"Testing Image {i}: {os.path.basename(img_path)}")
    print('='*50)
    
    if not os.path.exists(img_path):
        print(f"ERROR: Image not found at {img_path}")
        continue
        
    result = pipeline.process(img_path)
    
    print(f"\nDetected Drug Name: {result['fields']['drug_name']['value']}")
    print(f"Confidence: {result['fields']['drug_name']['confidence']*100:.2f}%")
    print("-" * 20)
    print(f"Detected Barcode: {result['fields']['barcode']['value']}")
    print("-" * 20)
    print(f"FDA Verified: {result['verification']['matched_source'] is not None}")
    
    if result['verification']['matched_source']:
        print(f"Match Score: {result['verification']['match_score']:.2f}")
        print(f"RxNorm CUI: {result['verification']['rxcui']}")
        if result['fields']['meta'].get('manufacturer'):
            print(f"Manufacturer: {result['fields']['meta']['manufacturer']}")
    
    print('='*50)
