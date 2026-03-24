# backend/services/recording_manager.py
import os
import cv2
import time
import threading
from collections import deque
from backend.utils.hash_utils import generate_hash, generate_chain_hash
import logging

logger = logging.getLogger("SentinelAI")

class RecordingManager:
    """
    Handles per-student rolling buffer, snapshot, and short video clip recording.
    """

    def __init__(self, evidence_dir, evidence_lock, buffer_sec=5, fps=10):
        self.buffers = {}  # student_id -> deque of frames
        self.buffer_sec = buffer_sec
        self.fps = fps
        self.max_frames = buffer_sec * fps
        self.lock = threading.Lock()
        self.evidence_dir = evidence_dir
        self.evidence_lock = evidence_lock

    def add_frame(self, student_id, frame):
        """Add a frame to the per-student rolling buffer"""
        with self.lock:
            if student_id not in self.buffers:
                self.buffers[student_id] = deque(maxlen=self.max_frames)
            self.buffers[student_id].append((frame.copy(), int(time.time())))

    def save_snapshot(self, student_id, frame, event_type):
        """Save a single snapshot image and compute its hash"""
        timestamp = int(time.time())
        filename = f"{student_id}_{event_type}_{timestamp}.jpg"
        path = os.path.join(self.evidence_dir, filename)
        with self.evidence_lock:
            cv2.imwrite(path, frame)
            file_hash = generate_hash(path)
        logger.info(f"Snapshot saved: {filename}")
        return filename, timestamp, file_hash

    def save_clip(self, student_id, event_type):
        """Save a short video clip from the rolling buffer"""
        with self.lock:
            if student_id not in self.buffers or len(self.buffers[student_id]) == 0:
                return None, None, None
            frames = list(self.buffers[student_id])

        timestamp = int(time.time())
        filename = f"{student_id}_{event_type}_{timestamp}.mp4"
        path = os.path.join(self.evidence_dir, filename)
        height, width = frames[0][0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(path, fourcc, self.fps, (width, height))

        for f, _ in frames:
            out.write(f)
        out.release()

        with self.evidence_lock:
            file_hash = generate_hash(path)
        logger.info(f"Clip saved: {filename}")
        return filename, timestamp, file_hash

    def save_event(self, student_id, frame, event_type):
        """
        Save both snapshot and rolling clip for an event.
        Returns dict with filenames and hashes.
        """
        snapshot_file, _, snapshot_hash = self.save_snapshot(student_id, frame, event_type)
        clip_file, _, clip_hash = self.save_clip(student_id, event_type)
        return {
            "snapshot_file": snapshot_file,
            "clip_file": clip_file,
            "snapshot_hash": snapshot_hash,
            "clip_hash": clip_hash
        }
