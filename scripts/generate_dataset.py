import os
import cv2
import json
import random
import numpy as np

DATASET_DIR = "../dataset/images"
ANNOTATION_FILE = "../dataset/annotations/labels.json"

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
    for cls in CLASSES:
        os.makedirs(os.path.join(DATASET_DIR, cls), exist_ok=True)


def generate_image(label):
    img = np.ones((224, 224, 3), dtype=np.uint8) * 255

    color = (0, 0, 255)

    text_map = {
        "phone_usage": "PHONE",
        "multiple_faces": "2 FACES",
        "no_face": "NO FACE",
        "looking_away": "LOOK AWAY",
        "book_usage": "BOOK",
        "impersonation": "IMPOSTER",
        "obstruction": "BLOCKED",
        "audio_cheating": "AUDIO",
        "tab_switch": "TAB SWITCH"
    }

    if label in text_map:
        cv2.putText(img, text_map[label], (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    return img


def generate_dataset(n=200):
    annotations = []

    for i in range(n):
        label = random.choice(CLASSES)

        img = generate_image(label)

        filename = f"{label}_{i}.jpg"
        path = os.path.join(DATASET_DIR, label, filename)

        cv2.imwrite(path, img)

        annotations.append({
            "file": path,
            "label": label
        })

    with open(ANNOTATION_FILE, "w") as f:
        json.dump(annotations, f, indent=4)

    print("✅ Dataset generated:", n)


if __name__ == "__main__":
    create_dirs()
    generate_dataset(300)
