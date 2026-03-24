# backend/services/multi_camera_manager.py

import time
import json
import logging
import random
import base64
from pathlib import Path
from threading import Lock, Thread
import cv2
import numpy as np

from backend.engine.event_engine import event_engine
from backend.services.recording_manager import RecordingManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiCameraManager:
    """
    Simulates multiple camera streams for demo purposes.
    Pushes frames to EventEngine and RecordingManager.
    """

    def __init__(self, 
                 registry_path: str = "backend/config/camera_registry.json",
                 resize_width: int = 640,
                 recording_manager: RecordingManager = None):
        self.registry_path = registry_path
        self.resize_width = resize_width
        self.frame_lock = Lock()
        self.frames = {}           # cam_id -> latest frame dict
        self.student_alerts = {}   # student_id -> last alert
        self.running = False
        self.cameras = {}          # cam_id -> list of frames for simulation
        self.metadata = {}         # cam_id -> student info
        self.recording_manager = recording_manager
        self._load_registry()
        self._prepare_simulation_frames()

    def _load_registry(self):
        """Load camera registry JSON"""
        try:
            with open(self.registry_path, "r") as f:
                data = json.load(f)

            for student in data.get("students", []):
                cam_id = student.get("camera_id")
                student_id = student.get("student_id")
                self.metadata[cam_id] = {"student_id": student_id}
                self.cameras[cam_id] = []  # to be filled with frames
            logger.info(f"[MultiCameraManager] Loaded {len(self.cameras)} cameras")
        except Exception as e:
            logger.error(f"[MultiCameraManager] Failed to load registry: {e}")

    def _prepare_simulation_frames(self):
        """Load demo frames for simulation"""
        base_path = Path("simulation_data/demo_frames")
        all_frames = sorted(base_path.glob("*.jpg"))
        if not all_frames:
            logger.warning("[MultiCameraManager] No simulation frames found! Using black frames.")

        for cam_id in self.cameras:
            self.cameras[cam_id] = all_frames  # same frames for demo
            self.frames[cam_id] = {
                "frame": self._black_frame_base64(),
                "timestamp": time.time(),
                "student_id": self.metadata[cam_id]["student_id"]
            }

    def _black_frame(self):
        return np.zeros((480, 640, 3), dtype=np.uint8)

    def _black_frame_base64(self):
        _, buffer = cv2.imencode(".jpg", self._black_frame())
        return base64.b64encode(buffer).decode()

    def start_all(self):
        """Start all simulated camera feeds"""
        self.running = True
        for cam_id in self.cameras:
            t = Thread(target=self._simulate_camera_feed, args=(cam_id,), daemon=True)
            t.start()
        logger.info("[MultiCameraManager] All cameras started")

    def stop_all(self):
        self.running = False
        logger.info("[MultiCameraManager] All cameras stopped")

    def _simulate_camera_feed(self, cam_id: str):
        """Simulate live camera feed"""
        frames_list = self.cameras[cam_id]
        idx = 0
        while self.running:
            if frames_list:
                frame_path = frames_list[idx % len(frames_list)]
                frame = cv2.imread(str(frame_path))
                if frame is not None:
                    frame = cv2.resize(frame, (self.resize_width, int(frame.shape[0]*self.resize_width/frame.shape[1])))
                    # overlay alert if exists
                    frame = self._overlay_alerts(frame, cam_id)
                    student_id = self.metadata[cam_id]["student_id"]

                    # Add frame to RecordingManager
                    if self.recording_manager:
                        self.recording_manager.add_frame(student_id, frame)

                    # Encode to base64 for EventEngine
                    _, buffer = cv2.imencode(".jpg", frame)
                    b64_frame = base64.b64encode(buffer).decode()

                    # Update frame in MultiCameraManager
                    with self.frame_lock:
                        self.frames[cam_id]["frame"] = b64_frame
                        self.frames[cam_id]["timestamp"] = time.time()

                    # Update EventEngine
                    event_engine.update_frame(student_id, b64_frame)
                    event = event_engine.process_frame(student_id, frame)
                    # Store latest student alert
                    with self.frame_lock:
                        self.student_alerts[student_id] = event

                idx += 1

            # Random demo alert
            if random.random() > 0.85:
                student_id = self.metadata[cam_id]["student_id"]
                alert_type = random.choice(["multiple_faces", "looking_away", "phone_detected"])
                snapshot = self.frames[cam_id]["frame"]
                with self.frame_lock:
                    self.student_alerts[student_id] = {
                        "student_id": student_id,
                        "alert_type": alert_type,
                        "timestamp": time.time(),
                        "snapshot": snapshot
                    }
            time.sleep(0.5)  # 500ms per frame

    def _overlay_alerts(self, frame, cam_id):
        """Draw overlays on frame"""
        student_id = self.metadata[cam_id]["student_id"]
        if student_id in self.student_alerts:
            alert = self.student_alerts[student_id]
            cv2.putText(frame, f"⚠ {alert['alert_type']}", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, f"{student_id} | {time.strftime('%H:%M:%S')}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        return frame

    # --- API methods ---
    def get_frame(self, cam_id: str):
        with self.frame_lock:
            return self.frames.get(cam_id, {
                "frame": self._black_frame_base64(),
                "timestamp": time.time(),
                "student_id": self.metadata.get(cam_id, {}).get("student_id")
            })

    def get_all_frames(self):
        with self.frame_lock:
            return self.frames.copy()

    def get_all_student_alerts(self):
        with self.frame_lock:
            return self.student_alerts.copy()


# --- Demo usage ---
if __name__ == "__main__":
    from backend.services.recording_manager import RecordingManager
    import os

    # create demo recording manager
    recording_manager = RecordingManager(evidence_dir="demo_evidence", evidence_lock=Lock(), buffer_sec=5, fps=10)
    manager = MultiCameraManager(recording_manager=recording_manager)
    manager.start_all()

    try:
        while True:
            frames = manager.get_all_frames()
            for cam_id, data in frames.items():
                b64_frame = data["frame"]
                nparr = np.frombuffer(base64.b64decode(b64_frame), np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                cv2.imshow(f"{cam_id}", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            time.sleep(0.02)
    except KeyboardInterrupt:
        pass
    finally:
        manager.stop_all()
        cv2.destroyAllWindows()
