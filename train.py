from pathlib import Path
from ultralytics import YOLO

PROJECT_DIR = Path.home() / "DisasterResponseSystem"

# Load pretrained YOLO11 nano weights.
model = YOLO("yolo11n.pt")

# Fine-tune on our person-and-dog dataset.
results = model.train(
    data=str(PROJECT_DIR / "dataset" / "data.yaml"),
    epochs=30,
    imgsz=640,
    batch=8,
    patience=8,
    workers=2,
    project=str(PROJECT_DIR / "runs"),
    name="disaster_detector",
    exist_ok=True,
    plots=True,
    seed=42
)

print("\nTraining finished.")
print(f"Training results are saved in: {PROJECT_DIR / 'runs'}")
print("Look for the best.pt model in:")
print(PROJECT_DIR / "runs" / "disaster_detector" / "weights" / "best.pt")
