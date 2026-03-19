import os
import cv2
import json
import random
import numpy as np
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)

IMAGE_DIR = os.path.join(BASE_DIR, "images")
ANNOTATION_DIR = os.path.join(BASE_DIR, "annotations")
ANNOTATION_FILE = os.path.join(ANNOTATION_DIR, "labels.json")

CLASSES = [
    "normal",
    "phone_usage",
    "multiple_faces",
    "no_face",
    "looking_away",
    "book_usage",
    "impersonation",
    "obstruction",
    "audio_cheating",
    "tab_switch"
]


def create_dirs():
    os.makedirs(ANNOTATION_DIR, exist_ok=True)

    for cls in CLASSES:
        os.makedirs(os.path.join(IMAGE_DIR, cls), exist_ok=True)


def draw_event_overlay(img, label):
    h, w, _ = img.shape

    color_map = {
        "phone_usage": (0, 0, 255),
        "multiple_faces": (255, 0, 0),
        "looking_away": (0, 255, 255),
        "book_usage": (255, 255, 0),
        "impersonation": (255, 0, 255),
        "obstruction": (0, 0, 0),
        "audio_cheating": (0, 128, 255),
        "tab_switch": (128, 0, 255)
    }

    if label != "normal":
        color = color_map.get(label, (0, 0, 255))

        cv2.putText(
            img,
            label.upper(),
            (20, h // 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2
        )

    return img


def generate_base_image():
    # random background
    img = np.ones((224, 224, 3), dtype=np.uint8) * random.randint(180, 255)

    # simulate face (circle)
    cv2.circle(img, (112, 80), 30, (0, 0, 0), 2)

    return img


def generate_sample(label):
    img = generate_base_image()

    # simulate variations
    if label == "multiple_faces":
        cv2.circle(img, (60, 80), 20, (0, 0, 0), 2)

    if label == "no_face":
        img = np.ones((224, 224, 3), dtype=np.uint8) * 255

    if label == "obstruction":
        img[:] = random.randint(0, 30)

    img = draw_event_overlay(img, label)

    return img


def generate_dataset(num_samples=500):
    annotations = []

    for i in range(num_samples):
        label = random.choice(CLASSES)

        img = generate_sample(label)

        filename = f"{label}_{i}.jpg"
        path = os.path.join(IMAGE_DIR, label, filename)

        cv2.imwrite(path, img)

        annotations.append({
            "file": path,
            "label": label,
            "timestamp": datetime.utcnow().isoformat()
        })

    with open(ANNOTATION_FILE, "w") as f:
        json.dump(annotations, f, indent=4)

    print(f"✅ Generated {num_samples} samples")


if __name__ == "__main__":
    create_dirs()
    generate_dataset(800)
