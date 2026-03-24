# scripts/generate_dataset.py
import os
import sys
import json
import csv
import random
from pathlib import Path

# -----------------------------
# Fix imports by adding project root
# -----------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

# Import synthetic generator from backend
from backend.synthetic_generator import create_dirs, generate_dataset

# -----------------------------
# BASE DIRECTORIES
# -----------------------------
BASE_DIR = os.path.join(PROJECT_ROOT, "backend")
DATASET_DIR = os.path.join(BASE_DIR, "dataset")

IMAGE_DIR = os.path.join(DATASET_DIR, "images")
VIDEO_DIR = os.path.join(DATASET_DIR, "videos")
AUDIO_DIR = os.path.join(DATASET_DIR, "audio")
ANNOTATION_DIR = os.path.join(DATASET_DIR, "annotations")

# Ensure annotation directory exists
os.makedirs(ANNOTATION_DIR, exist_ok=True)

# -----------------------------
# Files
# -----------------------------
JSON_FILE = os.path.join(ANNOTATION_DIR, "labels.json")
CSV_FILE = os.path.join(ANNOTATION_DIR, "events.csv")
TRAIN_FILE = os.path.join(ANNOTATION_DIR, "train.txt")
VAL_FILE = os.path.join(ANNOTATION_DIR, "val.txt")

# Train/Val split
TRAIN_SPLIT = 0.8

# -----------------------------
# Create CSV from JSON
# -----------------------------
def json_to_csv():
    if not os.path.exists(JSON_FILE):
        print(f"⚠ JSON file not found: {JSON_FILE}")
        return

    with open(JSON_FILE, "r") as f:
        data = json.load(f)

    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "label"])

        for item in data:
            writer.writerow([item["file"], item["label"]])

    print("✅ CSV annotations created")

# -----------------------------
# Train/Validation Split
# -----------------------------
def split_dataset():
    if not os.path.exists(JSON_FILE):
        print(f"⚠ JSON file not found: {JSON_FILE}")
        return

    with open(JSON_FILE, "r") as f:
        data = json.load(f)

    random.shuffle(data)
    split_idx = int(len(data) * TRAIN_SPLIT)
    train_data = data[:split_idx]
    val_data = data[split_idx:]

    # Write train.txt
    with open(TRAIN_FILE, "w") as f:
        for item in train_data:
            f.write(f"{item['file']} {item['label']}\n")

    # Write val.txt
    with open(VAL_FILE, "w") as f:
        for item in val_data:
            f.write(f"{item['file']} {item['label']}\n")

    print(f"✅ Train samples: {len(train_data)}")
    print(f"✅ Validation samples: {len(val_data)}")

# -----------------------------
# Verify Dataset
# -----------------------------
def verify_dataset():
    if not os.path.exists(JSON_FILE):
        print(f"⚠ JSON file not found: {JSON_FILE}")
        return

    missing = 0
    with open(JSON_FILE, "r") as f:
        data = json.load(f)

    for item in data:
        if not os.path.exists(item["file"]):
            missing += 1

    print(f"🔍 Missing files: {missing}")
    print(f"📊 Total files: {len(data)}")

# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":
    print("\n🚀 Generating Dataset...\n")

    # 1️⃣ Create required directories
    create_dirs()

    # 2️⃣ Generate images, audio, and video
    generate_dataset(n_images=500, n_videos=20)

    # 3️⃣ Create CSV and annotation files
    json_to_csv()

    # 4️⃣ Train/Validation split
    split_dataset()

    # 5️⃣ Verify all files exist
    verify_dataset()

    print("\n✅ DATASET PIPELINE COMPLETE\n")