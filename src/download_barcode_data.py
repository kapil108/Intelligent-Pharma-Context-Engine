from roboflow import Roboflow
import os

def download_dataset(api_key):
    rf = Roboflow(api_key=api_key)
    project = rf.workspace("tj1016-6mzid").project("barcode-detection-sv5m7")
    version = project.version(1)
    dataset = version.download("yolov8", location=os.path.join("data", "barcode_real"))
    print(f"Dataset downloaded to {dataset.location}")

if __name__ == "__main__":
    download_dataset("xXEHubVWR0CeQnD583R9")
