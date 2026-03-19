import os
import sys
import json
import csv
import random
from pathlib import Path

# Add dataset folder to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "dataset"))

from synthetic_generator import create_dirs, generate_dataset

# -----------------------------
# CONFIG
# -----------------------------
DATASET_DIR = "../dataset"
ANNOTATION_DIR = os.path.join(DATASET_DIR, "annotations")
IMAGE_DIR = os.path.join(DATASET_DIR, "images")

TRAIN_SPLIT = 0.8

JSON_FILE = os.path.join(ANNOTATION_DIR, "labels.json")
CSV_FILE = os.path.join(ANNOTATION_DIR, "events.csv")


# -----------------------------
# CREATE CSV FROM JSON
# -----------------------------
def json_to_csv():
    with open(JSON_FILE, "r") as f:
        data = json.load(f)

    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "label"])

        for item in data:
            writer.writerow([item["file"], item["label"]])

    print("✅ CSV annotations created")


# -----------------------------
# TRAIN / VAL SPLIT
# -----------------------------
def split_dataset():
    train_file = os.path.join(ANNOTATION_DIR, "train.txt")
    val_file = os.path.join(ANNOTATION_DIR, "val.txt")

    with open(JSON_FILE, "r") as f:
        data = json.load(f)

    random.shuffle(data)

    split_idx = int(len(data) * TRAIN_SPLIT)

    train_data = data[:split_idx]
    val_data = data[split_idx:]

    with open(train_file, "w") as f:
        for item in train_data:
            f.write(f"{item['file']} {item['label']}\n")

    with open(val_file, "w") as f:
        for item in val_data:
            f.write(f"{item['file']} {item['label']}\n")

    print(f"✅ Train samples: {len(train_data)}")
    print(f"✅ Validation samples: {len(val_data)}")


# -----------------------------
# VERIFY DATASET
# -----------------------------
def verify_dataset():
    missing = 0

    with open(JSON_FILE, "r") as f:
        data = json.load(f)

    for item in data:
        if not os.path.exists(item["file"]):
            missing += 1

    print(f"🔍 Missing files: {missing}")
    print(f"📊 Total files: {len(data)}")


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("\n🚀 Generating Dataset...\n")

    create_dirs()
    generate_dataset(800)

    json_to_csv()
    split_dataset()
    verify_dataset()

    print("\n✅ DATASET PIPELINE COMPLETE\n")
