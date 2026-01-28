import cv2
import numpy as np

class ImagePreprocessor:
    def __init__(self):
        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        # This solves the "Specular Glare" hurdle on foil strips.
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

    def remove_glare(self, image):
        """Converts to LAB color space to equalize lightness without distorting color."""
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l2 = self.clahe.apply(l)
        lab = cv2.merge((l2, a, b))
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    def sharpen_text(self, image):
        """Applies a kernel to make text edges crisp for OCR."""
        kernel = np.array([[0, -1, 0],
                           [-1, 5,-1],
                           [0, -1, 0]])
        return cv2.filter2D(image, -1, kernel)

    def process(self, image_path):
        """The main pipeline for image cleanup."""
        img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED) # Load with alpha if present
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Handle Transparency (Alpha Channel) -> Convert to White Background
        if img.shape[2] == 4:
            trans_mask = img[:,:,3] == 0
            img[trans_mask] = [255, 255, 255, 255]
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        # 1. Resize if too large (improves speed)
        if img.shape[1] > 1024:
            scale_percent = 1024 / img.shape[1]
            width = int(img.shape[1] * scale_percent)
            height = int(img.shape[0] * scale_percent)
            img = cv2.resize(img, (width, height))

        # 2. Remove Glare
        no_glare = self.remove_glare(img)
        
        # 3. Sharpen
        clean_img = self.sharpen_text(no_glare)
        
        return clean_img
