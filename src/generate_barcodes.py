import os
import random
import cv2
import numpy as np
import barcode
from barcode.writer import ImageWriter

# Setup Directories
BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "barcode_synthetic")
TRAIN_IMG = os.path.join(BASE_DIR, "train", "images")
TRAIN_LBL = os.path.join(BASE_DIR, "train", "labels")
VAL_IMG = os.path.join(BASE_DIR, "val", "images")
VAL_LBL = os.path.join(BASE_DIR, "val", "labels")

for d in [TRAIN_IMG, TRAIN_LBL, VAL_IMG, VAL_LBL]:
    os.makedirs(d, exist_ok=True)

def create_barcode_image(code_type, code_value):
    """Generate a barcode image using python-barcode."""
    writer = ImageWriter()
    # Write to a temporary file-like object or save temp
    # simpler to save and read back with cv2
    temp_filename = "temp_barcode"
    BARCODE = barcode.get_barcode_class(code_type)
    my_code = BARCODE(code_value, writer=writer)
    filename = my_code.save(temp_filename) # saves as temp_barcode.png
    
    img = cv2.imread(filename)
    os.remove(filename) # cleanup
    return img

def add_noise(img):
    """Add some salt/pepper or gaussian noise."""
    row, col, ch = img.shape
    mean = 0
    var = 0.1
    sigma = var**0.5
    gauss = np.random.normal(mean, sigma, (row, col, ch))
    gauss = gauss.reshape(row, col, ch)
    noisy = img + gauss * 50
    return np.clip(noisy, 0, 255).astype(np.uint8)

def generate_sample(index, split_dir_img, split_dir_lbl):
    # 1. Background
    bg_w, bg_h = 640, 640
    background = np.ones((bg_h, bg_w, 3), dtype=np.uint8) * 255
    # Add some random colored patches/noise to simulate label clutter
    for _ in range(5):
        x = random.randint(0, bg_w)
        y = random.randint(0, bg_h)
        cv2.circle(background, (x, y), random.randint(10, 100), (random.randint(200,255), random.randint(200,255), random.randint(200,255)), -1)

    # 2. Generate Barcode
    code_type = random.choice(['ean13', 'code128', 'upc'])
    # random 12 digit number
    val = "".join([str(random.randint(0, 9)) for _ in range(12)]) 
    try:
        bc_img = create_barcode_image(code_type, val)
    except:
        # fallback simple
        bc_img = create_barcode_image('code128', val)

    # Scale barcode
    scale = random.uniform(0.5, 1.2)
    bc_img = cv2.resize(bc_img, None, fx=scale, fy=scale)
    h, w, _ = bc_img.shape

    # 3. Place on Background
    # random position
    x_offset = random.randint(0, bg_w - w)
    y_offset = random.randint(0, bg_h - h)
    
    roi = background[y_offset:y_offset+h, x_offset:x_offset+w]
    # Simple alpha blending if needed, but barcode is opaque white bg usually
    background[y_offset:y_offset+h, x_offset:x_offset+w] = bc_img

    # 4. Save Image
    filename = f"barcode_{index:04d}.jpg"
    cv2.imwrite(os.path.join(split_dir_img, filename), background)

    # 5. Create YOLO Label
    # class x_center y_center width height (normalized)
    cls_id = 0 # 'barcode'
    cx = (x_offset + w / 2) / bg_w
    cy = (y_offset + h / 2) / bg_h
    nw = w / bg_w
    nh = h / bg_h
    
    label_file = filename.replace('.jpg', '.txt')
    with open(os.path.join(split_dir_lbl, label_file), 'w') as f:
        f.write(f"{cls_id} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}\n")

if __name__ == "__main__":
    print("Generating training data...")
    for i in range(100): # 100 training images
        generate_sample(i, TRAIN_IMG, TRAIN_LBL)
    
    print("Generating validation data...")
    for i in range(20): # 20 validation images
        generate_sample(i, VAL_IMG, VAL_LBL)

    # Create dataset.yaml
    yaml_content = f"""
path: ../data/barcode_synthetic
train: train/images
val: val/images

nc: 1
names: ['barcode']
"""
    yaml_path = os.path.join(BASE_DIR, "data.yaml")
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    print(f"Done. Dataset created at {BASE_DIR}")
