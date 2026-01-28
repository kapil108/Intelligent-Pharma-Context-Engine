from PIL import Image
import os
import shutil

# Source images
source_images = [
    r"C:/Users/kapil/.gemini/antigravity/brain/061f6500-0ec4-414a-9ce9-f0e4843372f6/uploaded_media_0_1769623806938.jpg",
    r"C:/Users/kapil/.gemini/antigravity/brain/061f6500-0ec4-414a-9ce9-f0e4843372f6/uploaded_media_1_1769623806938.jpg",
    r"C:/Users/kapil/.gemini/antigravity/brain/061f6500-0ec4-414a-9ce9-f0e4843372f6/uploaded_media_2_1769623806938.jpg"
]

# Destination directory
train_img_dir = r"C:/Users/kapil/OneDrive/Desktop/Intelligent Pharma-Context Engine/repo/data/barcode_real_small/train/images"
train_lbl_dir = r"C:/Users/kapil/OneDrive/Desktop/Intelligent Pharma-Context Engine/repo/data/barcode_real_small/train/labels"

# Manual YOLO annotations (class_id, x_center, y_center, width, height) - all normalized 0-1
# These are estimated based on visual inspection of the images
annotations = [
    # Image 0: Vertical vial - barcode is on the middle-right side
    "0 0.65 0.50 0.25 0.30",
    
    # Image 1: Horizontal ampoule - barcode is on the left label area
    "0 0.30 0.55 0.25 0.35",
    
    # Image 2: Test tube - barcode is on the center label
    "0 0.50 0.60 0.60 0.25"
]

for i, (src_img, annotation) in enumerate(zip(source_images, annotations)):
    # Copy image
    dest_img = os.path.join(train_img_dir, f"custom_ampoule_{i}.jpg")
    shutil.copy(src_img, dest_img)
    print(f"Copied {os.path.basename(src_img)} to {dest_img}")
    
    # Create label file
    dest_lbl = os.path.join(train_lbl_dir, f"custom_ampoule_{i}.txt")
    with open(dest_lbl, 'w') as f:
        f.write(annotation + "\n")
    print(f"Created label {dest_lbl}")

print("\nDone! Added 3 custom images to training dataset.")
