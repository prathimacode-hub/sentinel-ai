# backend/detection/objects.py
import os
import random
import numpy as np

# -----------------------------
# TRY YOLOv8
# -----------------------------
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
    print("✅ YOLO available for object detection")
except Exception as e:
    YOLO_AVAILABLE = False
    print("⚠ YOLO not installed → using simulation mode:", e)

# -----------------------------
# CONFIG
# -----------------------------
MODEL_DIR = "models/object_detection"
MODEL_PATH = os.path.join(MODEL_DIR, "yolov8.pt")
TARGET_OBJECTS = ["cell phone", "book", "laptop", "person", "bottle"]

# -----------------------------
# OBJECT DETECTOR CLASS
# -----------------------------
class ObjectDetector:
    def __init__(self):
        self.model = None
        os.makedirs(MODEL_DIR, exist_ok=True)

        if not YOLO_AVAILABLE:
            print("⚠ Running ObjectDetector in simulation mode")
            return

        try:
            # Load existing model if available
            if os.path.exists(MODEL_PATH):
                print("✅ Loading YOLO model from local path")
                self.model = YOLO(MODEL_PATH)
            else:
                print("⬇ Downloading YOLO model (yolov8n.pt)")
                self.model = YOLO("yolov8n.pt")  # Auto-download
                self.model.save(MODEL_PATH)

        except Exception as e:
            print("⚠ YOLO model loading failed:", e)
            self.model = None

    # -----------------------------
    # OBJECT DETECTION
    # -----------------------------
    def detect(self, frame):
        """
        Detect objects in a frame.
        Returns:
            list of dicts: [{"type": "object_alert", "value": True/False, "details": [...]}]
        """
        results_list = []

        # -----------------------------
        # SIMULATION / FALLBACK
        # -----------------------------
        if not YOLO_AVAILABLE or self.model is None:
            simulated_objects = random.sample(TARGET_OBJECTS, k=random.randint(0, 2))
            results_list.append({
                "type": "object_alert",
                "value": bool(simulated_objects),
                "details": simulated_objects,
                "mode": "simulated"
            })
            return results_list

        # -----------------------------
        # REAL DETECTION
        # -----------------------------
        try:
            results = self.model(frame)
            detected_objects = []

            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    label = self.model.names[cls_id]
                    if label in TARGET_OBJECTS:
                        detected_objects.append(label)

            results_list.append({
                "type": "object_alert",
                "value": bool(detected_objects),
                "details": detected_objects,
                "mode": "real"
            })
            return results_list

        except Exception as e:
            print("⚠ Object detection error:", e)
            results_list.append({
                "type": "object_alert",
                "value": False,
                "details": [],
                "mode": "error_fallback"
            })
            return results_list

    # -----------------------------
    # CAMERA OBSTRUCTION DETECTION
    # -----------------------------
    def detect_obstruction(self, frame):
        """
        Detect if camera is blocked (low brightness)
        Returns dict
        """
        try:
            brightness = np.mean(frame)
            return {
                "obstruction": brightness < 40,
                "brightness": float(brightness),
                "mode": "real"
            }
        except Exception as e:
            print("⚠ Obstruction detection error:", e)
            return {"obstruction": False, "brightness": 0, "mode": "error_fallback"}


# -----------------------------
# SINGLETON INSTANCE
# -----------------------------
object_detector = ObjectDetector()
