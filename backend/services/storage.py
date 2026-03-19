import os
import json
from datetime import datetime
from config import settings
from utils.hash_utils import generate_hash


class StorageManager:
    def __init__(self):
        self.base_dir = settings.EVIDENCE_DIR

        self.image_dir = os.path.join(self.base_dir, "images")
        self.video_dir = os.path.join(self.base_dir, "videos")
        self.audio_dir = os.path.join(self.base_dir, "audio")
        self.logs_dir = os.path.join(self.base_dir, "logs")

        self._create_dirs()

    def _create_dirs(self):
        for d in [self.image_dir, self.video_dir, self.audio_dir, self.logs_dir]:
            os.makedirs(d, exist_ok=True)

    # -----------------------------
    # IMAGE STORAGE
    # -----------------------------
    def save_image(self, frame, prefix="event"):
        import cv2

        filename = f"{prefix}_{int(datetime.utcnow().timestamp())}.jpg"
        path = os.path.join(self.image_dir, filename)

        cv2.imwrite(path, frame)

        return path

    # -----------------------------
    # VIDEO STORAGE
    # -----------------------------
    def save_video(self, frames, prefix="clip", fps=5):
        import cv2

        if not frames:
            return None

        filename = f"{prefix}_{int(datetime.utcnow().timestamp())}.avi"
        path = os.path.join(self.video_dir, filename)

        h, w, _ = frames[0].shape

        writer = cv2.VideoWriter(
            path,
            cv2.VideoWriter_fourcc(*'XVID'),
            fps,
            (w, h)
        )

        for f in frames:
            writer.write(f)

        writer.release()

        return path

    # -----------------------------
    # AUDIO STORAGE
    # -----------------------------
    def save_audio(self, audio_bytes, prefix="audio"):
        filename = f"{prefix}_{int(datetime.utcnow().timestamp())}.wav"
        path = os.path.join(self.audio_dir, filename)

        with open(path, "wb") as f:
            f.write(audio_bytes)

        return path

    # -----------------------------
    # EVENT LOG STORAGE
    # -----------------------------
    def save_event(self, event_data):
        filename = f"log_{int(datetime.utcnow().timestamp())}.json"
        path = os.path.join(self.logs_dir, filename)

        hash_val = generate_hash(event_data)

        data = {
            "event": event_data,
            "hash": hash_val,
            "timestamp": datetime.utcnow().isoformat()
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=4)

        return path, hash_val


# -----------------------------
# GLOBAL INSTANCE
# -----------------------------
storage = StorageManager()
