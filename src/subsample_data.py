import os
import shutil
import random
import yaml

def subsample_dataset(target_count=100):
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "barcode_real")
    
    # Original paths
    train_img_dir = os.path.join(base_dir, "train", "images")
    train_lbl_dir = os.path.join(base_dir, "train", "labels")
    
    # New paths for small dataset
    small_dir = os.path.join(os.path.dirname(base_dir), "barcode_real_small")
    os.makedirs(os.path.join(small_dir, "train", "images"), exist_ok=True)
    os.makedirs(os.path.join(small_dir, "train", "labels"), exist_ok=True)
    os.makedirs(os.path.join(small_dir, "valid", "images"), exist_ok=True)
    os.makedirs(os.path.join(small_dir, "valid", "labels"), exist_ok=True)

    # Get all images
    all_images = [f for f in os.listdir(train_img_dir) if f.endswith(('.jpg', '.png'))]
    
    if len(all_images) > target_count:
        selected = random.sample(all_images, target_count)
    else:
        selected = all_images
        
    print(f"Subsampling {len(selected)} images out of {len(all_images)}...")
    
    for img_name in selected:
        # Copy image
        shutil.copy(os.path.join(train_img_dir, img_name), 
                    os.path.join(small_dir, "train", "images", img_name))
        
        # Copy label
        lbl_name = img_name.rsplit('.', 1)[0] + ".txt"
        src_lbl = os.path.join(train_lbl_dir, lbl_name)
        if os.path.exists(src_lbl):
            shutil.copy(src_lbl, os.path.join(small_dir, "train", "labels", lbl_name))

    # Copy validation set (keep small)
    val_img_dir = os.path.join(base_dir, "valid", "images")
    val_lbl_dir = os.path.join(base_dir, "valid", "labels")
    val_images = [f for f in os.listdir(val_img_dir) if f.endswith(('.jpg', '.png'))][:20]
    
    for img_name in val_images:
        shutil.copy(os.path.join(val_img_dir, img_name), 
                    os.path.join(small_dir, "valid", "images", img_name))
        lbl_name = img_name.rsplit('.', 1)[0] + ".txt"
        src_lbl = os.path.join(val_lbl_dir, lbl_name)
        if os.path.exists(src_lbl):
            shutil.copy(src_lbl, os.path.join(small_dir, "valid", "labels", lbl_name))

    # Create data.yaml
    yaml_content = f"""
path: {small_dir.replace(os.sep, '/')}
train: train/images
val: valid/images

nc: 1
names: ['barcode']
"""
    with open(os.path.join(small_dir, "data.yaml"), 'w') as f:
        f.write(yaml_content)
        
    print(f"Created small dataset at {small_dir}")

if __name__ == "__main__":
    subsample_dataset()
