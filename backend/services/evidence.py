# backend/services/evidence.py

import cv2
import os
import time
import json
from datetime import datetime

# -----------------------------
# SAFE IMPORT (STEP 2 APPLIED)
# -----------------------------
try:
    from utils.hash_utils import generate_hash
    HASH_AVAILABLE = True
except Exception as e:
    print("⚠ Hash utils not found → using fallback hash")
    HASH_AVAILABLE = False

    def generate_hash(data):
        return "fallback_hash"


# -----------------------------
# DIRECTORY SETUP
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVIDENCE_DIR = os.path.join(BASE_DIR, "evidence")

os.makedirs(EVIDENCE_DIR, exist_ok=True)


# -----------------------------
# IMAGE EVIDENCE
# -----------------------------
def save_evidence(frame, event_level="event"):
    try:
        timestamp = int(time.time())
        filename = f"{event_level}_{timestamp}.jpg"
        filepath = os.path.join(EVIDENCE_DIR, filename)

        cv2.imwrite(filepath, frame)

        return filepath

    except Exception as e:
        print("❌ Error saving image:", e)
        return None


# -----------------------------
# VIDEO EVIDENCE
# -----------------------------
def save_video_clip(frames, event_level="event", fps=5):
    try:
        if not frames:
            return None

        timestamp = int(time.time())
        filename = f"{event_level}_{timestamp}.avi"
        filepath = os.path.join(EVIDENCE_DIR, filename)

        height, width, _ = frames[0].shape

        out = cv2.VideoWriter(
            filepath,
            cv2.VideoWriter_fourcc(*'XVID'),
            fps,
            (width, height)
        )

        for frame in frames:
            out.write(frame)

        out.release()

        return filepath

    except Exception as e:
        print("❌ Error saving video:", e)
        return None


# -----------------------------
# AUDIO EVIDENCE
# -----------------------------
def save_audio_clip(audio_bytes, event_level="event"):
    try:
        timestamp = int(time.time())
        filename = f"{event_level}_{timestamp}.wav"
        filepath = os.path.join(EVIDENCE_DIR, filename)

        with open(filepath, "wb") as f:
            f.write(audio_bytes)

        return filepath

    except Exception as e:
        print("❌ Error saving audio:", e)
        return None


# -----------------------------
# EVENT LOG (TAMPER-PROOF)
# -----------------------------
def save_event_log(event_data):
    try:
        timestamp = int(time.time())
        filename = f"log_{timestamp}.json"
        filepath = os.path.join(EVIDENCE_DIR, filename)

        # SAFE HASH
        log_hash = generate_hash(event_data)

        log_entry = {
            "event": event_data,
            "hash": log_hash,
            "created_at": datetime.utcnow().isoformat(),
            "hash_status": "enabled" if HASH_AVAILABLE else "fallback"
        }

        with open(filepath, "w") as f:
            json.dump(log_entry, f, indent=4)

        return filepath, log_hash

    except Exception as e:
        print("❌ Error saving log:", e)
        return None, None
    with open(filepath, "w") as f:
        json.dump(log_entry, f, indent=4)

    return filepath, log_hash
