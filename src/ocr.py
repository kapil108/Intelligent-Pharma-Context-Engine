import easyocr
import cv2
from pyzbar.pyzbar import decode
from pylibdmtx.pylibdmtx import decode as decode_dmtx
from .preprocess import dewarp_cylinder

class OCRSystem:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])

    def read_text(self, image, regions=None):
        """Read text from image or specific regions."""
        if regions:
            results = []
            for region in regions:
                x1, y1, x2, y2 = region['coords']
                crop = image[y1:y2, x1:x2]
                if crop.size == 0: continue
                text_results = self.reader.readtext(crop)
                results.extend(text_results)
            return results
        else:
            return self.reader.readtext(image)

    def read_barcodes(self, image):
        """Detect and decode Barcodes and DataMatrix with preprocessing."""
        
        def try_decode(img):
            res = []
            # 1D Barcodes
            try:
                for b in decode(img):
                    res.append({
                        "type": b.type,
                        "data": b.data.decode('utf-8'),
                        "rect": b.rect
                    })
            except Exception: pass
            
            # DataMatrix
            try:
                for d in decode_dmtx(img):
                    res.append({
                        "type": "DataMatrix",
                        "data": d.data.decode('utf-8'),
                        "rect": d.rect
                    })
            except Exception: pass
            return res

        # 1. Try Original
        results = try_decode(image)
        if results: return results
        
        # 2. Try Grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        results = try_decode(gray)
        if results: return results

        # 3. Try Thresholding (Binary)
        _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        results = try_decode(thresh)
        if results: return results
        
        # 4. Try Sharpening
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        results = try_decode(morph)
        if results: return results

        # 5. Try Adaptive Thresholding (good for lighting/curvature)
        adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        results = try_decode(adaptive)
        if results: return results

        # 6. Try Rotations (good for vertical/diagonal barcodes)
        rows, cols = gray.shape
        for angle in [90, -90, 45, -45]:
            M = cv2.getRotationMatrix2D((cols/2, rows/2), angle, 1)
            rotated = cv2.warpAffine(gray, M, (cols, rows))
            results = try_decode(rotated)
            if results: return results
            
        # 7. Try Dewarping (for curved ampoules)
        # We try dewarping the GRAYSCALE image
        dewarped = dewarp_cylinder(gray)
        results = try_decode(dewarped)
        if results: return results
        
        # 8. Try OpenCV BarcodeDetector (NEW - More robust than pyzbar)
        try:
            detector = cv2.barcode.BarcodeDetector()
            ret, decoded_info, decoded_type, points = detector.detectAndDecode(image)
            if ret and decoded_info:
                for info, btype in zip(decoded_info, decoded_type):
                    if info:  # Skip empty detections
                        results.append({
                            "type": btype,
                            "data": info,
                            "rect": None  # OpenCV doesn't provide rect in same format
                        })
                        print(f"[OpenCV Barcode] Found: {info} (type: {btype})")
                if results: return results
        except Exception as e:
            print(f"[OpenCV Barcode] Error: {e}")
        
        # 9. Try OpenCV QR Code Detector
        try:
            qr_detector = cv2.QRCodeDetector()
            ret, decoded_info, points, straight_qrcode = qr_detector.detectAndDecodeMulti(image)
            if ret and decoded_info:
                for info in decoded_info:
                    if info:  # Skip empty
                        results.append({
                            "type": "QR_CODE",
                            "data": info,
                            "rect": None
                        })
                        print(f"[OpenCV QR] Found: {info}")
                if results: return results
        except Exception as e:
            print(f"[OpenCV QR] Error: {e}")
        
        return results

if __name__ == "__main__":
    pass
