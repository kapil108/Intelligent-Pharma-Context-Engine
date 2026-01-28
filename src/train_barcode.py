from ultralytics import YOLO
import os

def train_barcode_model():
    model = YOLO('yolov8n.pt') 

    # Ensure absolute path to data.yaml
    yaml_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "barcode_real_small", "data.yaml"))

    print(f"DEBUG: Using dataset config: {yaml_path}")
    
    # Train
    model.train(
        data=yaml_path,
        epochs=10,
        imgsz=640,
        batch=8,
        name='yolov8n_barcode',
        device='cpu'
    )
    
if __name__ == "__main__":
    train_barcode_model()
