import cv2
import os
import time
import json
from datetime import datetime
from utils.hash_utils import generate_hash
from config import settings

EVIDENCE_DIR = settings.EVIDENCE_DIR


def save_evidence(frame, event_level):
    """
    Save image evidence
    """
    timestamp = int(time.time())
    filename = f"{event_level}_{timestamp}.jpg"
    filepath = os.path.join(EVIDENCE_DIR, filename)

    cv2.imwrite(filepath, frame)

    return filepath


def save_video_clip(frames, event_level, fps=5):
    """
    Save short video clip (list of frames)
    """
    timestamp = int(time.time())
    filename = f"{event_level}_{timestamp}.avi"
    filepath = os.path.join(EVIDENCE_DIR, filename)

    if not frames:
        return None

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


def save_audio_clip(audio_bytes, event_level):
    """
    Save audio evidence
    """
    timestamp = int(time.time())
    filename = f"{event_level}_{timestamp}.wav"
    filepath = os.path.join(EVIDENCE_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(audio_bytes)

    return filepath


def save_event_log(event_data):
    """
    Save tamper-proof event log
    """
    timestamp = int(time.time())
    filename = f"log_{timestamp}.json"
    filepath = os.path.join(EVIDENCE_DIR, filename)

    # Generate hash
    log_hash = generate_hash(event_data)

    log_entry = {
        "event": event_data,
        "hash": log_hash,
        "created_at": datetime.utcnow().isoformat()
    }

    with open(filepath, "w") as f:
        json.dump(log_entry, f, indent=4)

    return filepath, log_hash
