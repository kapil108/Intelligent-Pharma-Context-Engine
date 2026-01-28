import os
from datasets import load_dataset
from roboflow import Roboflow
import argparse

def download_pills_dataset(output_path):
    print(f"Downloading Pills Inside Bottles dataset to {output_path}...")
    try:
        dataset = load_dataset("OUTLAW83/pills_inside_bottles", trust_remote_code=True)
        dataset.save_to_disk(output_path)
        print("Pills dataset downloaded successfully.")
    except Exception as e:
        print(f"Failed to download pills dataset: {e}")
        print("Skipping...")

def download_roboflow_dataset(api_key, workspace, project, version, output_path):
    print(f"Downloading Roboflow dataset {project} v{version}...")
    rf = Roboflow(api_key=api_key)
    project = rf.workspace(workspace).project(project)
    dataset = project.version(version).download("yolov8", location=output_path)
    print(f"Roboflow dataset downloaded to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download project datasets")
    parser.add_argument("--roboflow_key", type=str, help="Roboflow API Key")
    args = parser.parse_args()

    base_data_path = os.path.join("repo", "data")
    os.makedirs(base_data_path, exist_ok=True)

    # 1. HuggingFace Dataset
    pills_path = os.path.join(base_data_path, "pills_inside_bottles")
    if not os.path.exists(pills_path):
        download_pills_dataset(pills_path)
    else:
        print("Pills dataset already exists.")

    # 2. Roboflow Dataset
    roboflow_dir = os.path.join(base_data_path, "roboflow_medicine_bottle")
    if args.roboflow_key:
        download_roboflow_dataset(
            api_key=args.roboflow_key,
            workspace="project-ko6pf",
            project="medicine-bottle",
            version=1, # Adjust version if known
            output_path=roboflow_dir
        )
    else:
        print("Skipping Roboflow download (no API key provided).")
        print(f"Please download manually from: https://universe.roboflow.com/project-ko6pf/medicine-bottle")
