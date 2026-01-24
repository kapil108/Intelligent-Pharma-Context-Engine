from ultralytics import YOLO
import cv2
import os

class Detector:
    def __init__(self, model_path=None):
        if model_path is None:
            # Look for locally trained barcode model
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # repo root
            custom_weights = os.path.join(base_dir, "runs", "detect", "yolov8n_barcode6", "weights", "best.pt")
            
            if os.path.exists(custom_weights):
                print(f"Loading custom barcode model: {custom_weights}")
                model_path = custom_weights
            else: 
                # Fallback or original
                model_path = os.path.join(base_dir, "models", "best_bottle_model.pt")
                if not os.path.exists(model_path):
                     model_path = "yolov8n.pt" # Last resort
        
        self.model = YOLO(model_path)

    def detect_regions(self, image):
        """Detect potential text and barcode regions."""
        results = self.model(image)
        regions = []
        
        for result in results:
            for box in result.boxes:
                coords = box.xyxy[0].tolist() # [x1, y1, x2, y2]
                label = result.names[int(box.cls[0])]
                conf = float(box.conf[0])
                regions.append({
                    "coords": [int(c) for c in coords],
                    "label": label,
                    "confidence": conf
                })
        
        return regions

if __name__ == "__main__":
    # Placeholder for testing
    pass
