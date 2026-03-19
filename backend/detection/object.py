from ultralytics import YOLO

# Load YOLO model (lightweight for hackathon)
model = YOLO("yolov8n.pt")

TARGET_OBJECTS = [
    "cell phone",
    "book",
    "laptop",
    "person"
]

def detect_objects(frame):
    """
    Detect objects like phone, book, etc.
    """
    results = model(frame, verbose=False)

    detected_objects = []

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]

            if label in TARGET_OBJECTS:
                detected_objects.append(label)

    return {
        "objects": detected_objects,
        "object_count": len(detected_objects)
    }

def detect_obstruction(frame):
    brightness = np.mean(frame)

    return {
        "obstruction": brightness < 40
    }
