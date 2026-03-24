# backend/synthetic_generator.py
import os
import cv2
import json
import csv
import random
import numpy as np
import wave
from datetime import datetime

# -----------------------------
# BASE DIRECTORY
# -----------------------------
BASE_DIR = os.path.join(os.path.dirname(__file__), "dataset")

# -----------------------------
# DATASET DIRECTORIES
# -----------------------------
IMAGE_DIR = os.path.join(BASE_DIR, "images")
VIDEO_DIR = os.path.join(BASE_DIR, "videos")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
ANNOTATION_DIR = os.path.join(BASE_DIR, "annotations")

# Ensure directories exist
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(ANNOTATION_DIR, exist_ok=True)

# -----------------------------
# JSON / CSV FILES
# -----------------------------
JSON_FILE = os.path.join(ANNOTATION_DIR, "labels.json")
CSV_FILE = os.path.join(ANNOTATION_DIR, "events.csv")

# -----------------------------
# CLASSES (10 MALPRACTICE EVENTS)
# -----------------------------
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

# Audio labels
AUDIO_CLASSES = ["silence", "speech", "noise"]

# -----------------------------
# CREATE DIRECTORIES
# -----------------------------
def create_dirs():
    for cls in CLASSES:
        os.makedirs(os.path.join(IMAGE_DIR, cls), exist_ok=True)

    os.makedirs(os.path.join(VIDEO_DIR, "normal_sessions"), exist_ok=True)
    os.makedirs(os.path.join(VIDEO_DIR, "cheating_sessions"), exist_ok=True)

    for a in AUDIO_CLASSES:
        os.makedirs(os.path.join(AUDIO_DIR, a), exist_ok=True)

    os.makedirs(ANNOTATION_DIR, exist_ok=True)

# -----------------------------
# IMAGE GENERATION
# -----------------------------
def generate_image(label):
    img = np.ones((224, 224, 3), dtype=np.uint8) * random.randint(180, 255)

    # Simulate a face if not "no_face"
    if label != "no_face":
        cv2.circle(img, (112, 80), 30, (0, 0, 0), 2)

    # Multiple faces simulation
    if label == "multiple_faces":
        cv2.circle(img, (60, 80), 20, (0, 0, 0), 2)

    # Obstruction simulation
    if label == "obstruction":
        img[:] = random.randint(0, 30)

    # Overlay label text
    cv2.putText(img, label, (10, 200),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

    return img

# -----------------------------
# AUDIO GENERATION
# -----------------------------
def generate_audio(label, filename):
    framerate = 44100
    duration = 2  # 2 seconds
    t = np.linspace(0, duration, int(framerate * duration))

    if label == "silence":
        signal = np.zeros_like(t)
    elif label == "speech":
        signal = np.sin(2 * np.pi * 220 * t)
    else:  # noise
        signal = np.random.randn(len(t))

    signal = (signal * 32767).astype(np.int16)
    path = os.path.join(AUDIO_DIR, label, filename)

    with wave.open(path, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(framerate)
        f.writeframes(signal.tobytes())

    return path

# -----------------------------
# VIDEO GENERATION
# -----------------------------
def generate_video(frames, path):
    h, w, _ = frames[0].shape
    writer = cv2.VideoWriter(
        path,
        cv2.VideoWriter_fourcc(*'XVID'),
        5,
        (w, h)
    )
    for f in frames:
        writer.write(f)
    writer.release()

# -----------------------------
# MAIN DATASET GENERATION
# -----------------------------
def generate_dataset(n_images=300, n_videos=10):
    annotations = []
    csv_rows = []

    # Generate images
    for i in range(n_images):
        label = random.choice(CLASSES)
        img = generate_image(label)
        filename = f"{label}_{i}.jpg"
        path = os.path.join(IMAGE_DIR, label, filename)
        cv2.imwrite(path, img)

        annotations.append({
            "file": path,
            "label": label,
            "timestamp": datetime.utcnow().isoformat()
        })
        csv_rows.append([path, label])

    # Generate audio
    for i in range(50):
        label = random.choice(AUDIO_CLASSES)
        generate_audio(label, f"{label}_{i}.wav")

    # Generate videos
    for i in range(n_videos):
        frames = []
        label = random.choice(CLASSES)
        for _ in range(20):
            frames.append(generate_image(label))
        folder = "cheating_sessions" if label != "normal" else "normal_sessions"
        video_path = os.path.join(VIDEO_DIR, folder, f"video_{i}.avi")
        generate_video(frames, video_path)

    # Save JSON
    with open(JSON_FILE, "w") as f:
        json.dump(annotations, f, indent=4)

    # Save CSV
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "label"])
        writer.writerows(csv_rows)

    print("✅ Dataset fully generated")

# -----------------------------
# RUN SCRIPT DIRECTLY
# -----------------------------
if __name__ == "__main__":
    create_dirs()
    generate_dataset(n_images=500, n_videos=20)
