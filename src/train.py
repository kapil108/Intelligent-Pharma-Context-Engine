from ultralytics import YOLO
import os

def train_model():
    # 1. Define paths
    dataset_yaml = os.path.join("repo", "data", "roboflow_medicine_bottle", "data.yaml")
    project_dir = os.path.join("repo", "results", "train")
    
    # 2. Check if dataset exists
    if not os.path.exists(dataset_yaml):
        print(f"Error: Dataset configuration file not found at {dataset_yaml}")
        print("Please ensure you have downloaded the dataset in YOLOv8 format.")
        return

    # 3. Load a model
    model = YOLO("yolov8n.pt")  # load a pretrained model (recommended for training)

    # 4. Train the model
    print("Starting training...")
    results = model.train(
        data=dataset_yaml, 
        epochs=50, 
        imgsz=640, 
        project=project_dir,
        name="medicine_bottle_v1"
    )
    
    print(f"Training completed. Models saved to {project_dir}")

if __name__ == "__main__":
    train_model()
