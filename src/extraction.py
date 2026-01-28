from easyocr import Reader
from pyzbar.pyzbar import decode
import cv2
import logging

class Extractor:
    def __init__(self):
        # Fallback to EasyOCR for robustness on this system
        # (PaddleOCR failed to install)
        self.reader = Reader(['en'], gpu=False) # Use CPU if GPU fails

    def get_barcode(self, image):
        """Decodes standard barcodes and QR codes."""
        decoded_objects = decode(image)
        for obj in decoded_objects:
            return obj.data.decode("utf-8") # Return the first found barcode
        return None

    def get_text(self, image):
        """Extracts all raw text with confidence scores."""
        # EasyOCR returns list of (bbox, text, prob)
        result = self.reader.readtext(image)
        raw_text = []
        for (bbox, text, prob) in result:
             # Filter out low-confidence noise
            if prob > 0.4: 
                raw_text.append(text)
        return raw_text
