from ultralytics import YOLO
import os

# Load YOLO model (lightweight for hackathon)
MODEL_PATH = "models/object_detection/yolov8.pt"

class ObjectDetector:
    def __init__(self):
        # Auto download if not present
        if not os.path.exists(MODEL_PATH):
            print("⬇ Downloading YOLO model...")
            self.model = YOLO("yolov8n.pt")   # auto-download
        else:
            print("✅ Loading local YOLO model...")
            self.model = YOLO(MODEL_PATH)

TARGET_OBJECTS = [
    "cell phone",
    "book",
    "laptop",
    "person"
]

def detect(self, frame):
    results = self.model(frame)

    detections = []
    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = self.model.names[cls_id]

            detections.append(label)

    return detections

def detect_obstruction(frame):
    brightness = np.mean(frame)

    return {
        "obstruction": brightness < 40
    }

# Singleton
object_detector = ObjectDetector()
