import cv2
import numpy as np

def remove_glare(image):
    """Apply CLAHE to mitigate glare and improve contrast."""
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    result = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return result

def dewarp_cylinder(image, focal_length=1000):
    """
    Applies an inverse cylindrical projection to 'unroll' the image.
    Assumes the image is a view of a vertical cylinder.
    """
    h, w = image.shape[:2]
    K = np.array([[focal_length, 0, w / 2],
                  [0, focal_length, h / 2],
                  [0, 0, 1]])  # Intrinsic matrix (estimated)

    # Creating the new image grid
    # We want to map destination pixels (flat) back to source pixels (curved)
    # x_flat = f * tan(theta) => theta = atan(x_flat / f)
    # x_cyl = f * sin(theta) => x_cyl = f * sin(atan(x_flat / f))
    
    # Let's try a simpler geometric heuristic: expand edges
    # Source x is roughly R * sin(x_dest/R) if strictly unrolling
    
    map_x = np.zeros((h, w), np.float32)
    map_y = np.zeros((h, w), np.float32)
    
    # Center x
    cx = w / 2
    # Radius approximation (width is roughly diameter? No, width is chord or arc)
    # Let's assume the image covers ~60 degrees of the cylinder
    # f * sin(30 deg) = w/2 => f * 0.5 = w/2 => f = w
    f = w 
    
    for y in range(h):
        for x in range(w):
            # Normalized x from center
            nx = (x - cx) / f 
            # Inverse project: x_src = f * tan(theta) -> this is for perspective
            # For cylinder unroll: x_dest is arc length -> x_src is projected x
            # x_src = f * sin(x_dest / f)
            
            x_src = f * np.sin(nx) + cx
            y_src = y # Assume vertical alignment
            
            map_x[y, x] = x_src
            map_y[y, x] = y_src

    return cv2.remap(image, map_x, map_y, cv2.INTER_LINEAR)

class Preprocessor:
    def process(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            return None
        
        img = remove_glare(img)
        # img = dewarp_cylinder(img) # Optional: Enable if always needed
        # For now, we keep it as a utility we can call from OCR fallback
        
        return img

if __name__ == "__main__":
    # Test with a dummy image if needed
    pass
