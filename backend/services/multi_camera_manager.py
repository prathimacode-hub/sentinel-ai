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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiCameraManager:
    """
    Simulates multiple camera streams (30 students) for demo purposes.
    Outputs base64 frames with optional AI alert events.
    """

    def __init__(self, registry_path: str = "backend/config/camera_registry.json", resize_width: int = 640):
        self.registry_path = registry_path
        self.resize_width = resize_width
        self.frame_lock = Lock()
        self.frames = {}           # camera_id -> latest frame dict
        self.alerts = {}           # camera_id -> last alert
        self.running = False
        self.cameras = {}          # camera_id -> video capture or frames list
        self.metadata = {}         # camera_id -> student info
        self._load_registry()
        self._prepare_simulation_frames()

    def _load_registry(self):
        """Load camera mapping from JSON file"""
        try:
            with open(self.registry_path, "r") as f:
                data = json.load(f)

            for student in data.get("students", []):
                cam_id = student.get("camera_id")
                student_id = student.get("student_id")
                self.metadata[cam_id] = {"student_id": student_id}
                self.cameras[cam_id] = []  # will be filled with demo frames

            logger.info(f"[MultiCameraManager] Loaded {len(self.cameras)} cameras from registry")
        except Exception as e:
            logger.error(f"[MultiCameraManager] Failed to load registry: {e}")

    def _prepare_simulation_frames(self):
        """
        Load demo frames from /simulation_data folder for each camera.
        Each camera has 20-50 frames to simulate live feed.
        """
        base_path = Path("simulation_data/demo_frames")
        all_frames = sorted(base_path.glob("*.jpg"))
        if not all_frames:
            logger.warning("[MultiCameraManager] No simulation frames found! Using black frames.")
        
        for cam_id in self.cameras:
            self.cameras[cam_id] = all_frames  # assign same frames for demo
            self.frames[cam_id] = {
                "frame": self._black_frame(),
                "timestamp": time.time(),
                "student_id": self.metadata[cam_id]["student_id"]
            }

    def _black_frame(self):
        return np.zeros((480, 640, 3), dtype=np.uint8)

    def start_all(self):
        """Start all simulated camera threads"""
        self.running = True
        for cam_id in self.cameras:
            t = Thread(target=self._simulate_camera_feed, args=(cam_id,), daemon=True)
            t.start()
        logger.info("[MultiCameraManager] All simulated cameras started")

    def stop_all(self):
        """Stop all simulation"""
        self.running = False
        logger.info("[MultiCameraManager] All cameras stopped")

    def _simulate_camera_feed(self, cam_id: str):
        """Simulate live feed for one camera"""
        frames_list = self.cameras[cam_id]
        idx = 0
        while self.running:
            if frames_list:
                frame_path = frames_list[idx % len(frames_list)]
                frame = cv2.imread(str(frame_path))
                if frame is not None:
                    frame = cv2.resize(frame, (self.resize_width, int(frame.shape[0] * self.resize_width / frame.shape[1])))
                    frame = self._overlay_alerts(frame, cam_id)
                    # encode to base64
                    _, buffer = cv2.imencode(".jpg", frame)
                    b64_frame = base64.b64encode(buffer).decode()
                    with self.frame_lock:
                        self.frames[cam_id]["frame"] = b64_frame
                        self.frames[cam_id]["timestamp"] = time.time()
                idx += 1

            # Random alert generation
            if random.random() > 0.85:
                alert_type = random.choice(["multiple_faces", "looking_away", "phone_detected"])
                timestamp = time.time()
                snapshot = self.frames[cam_id]["frame"]
                self.alerts[cam_id] = {
                    "student_id": self.metadata[cam_id]["student_id"],
                    "alert_type": alert_type,
                    "timestamp": timestamp,
                    "snapshot": snapshot
                }
            time.sleep(0.5)  # 500ms per frame

    def _overlay_alerts(self, frame, cam_id):
        """Draw demo overlays on frame"""
        if cam_id in self.alerts:
            alert = self.alerts[cam_id]
            cv2.putText(frame, f"⚠ {alert['alert_type']}", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(frame, f"{self.metadata[cam_id]['student_id']} | {time.strftime('%H:%M:%S')}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        return frame

    def get_frame(self, cam_id: str):
        """Return latest frame dict for WebSocket"""
        with self.frame_lock:
            return self.frames.get(cam_id, {
                "frame": self._black_frame(),
                "timestamp": time.time(),
                "student_id": self.metadata.get(cam_id, {}).get("student_id")
            })

    def get_all_frames(self):
        """Return all frames for dashboard"""
        with self.frame_lock:
            return self.frames.copy()

    def get_alerts(self):
        """Return latest alerts"""
        with self.frame_lock:
            return self.alerts.copy()


# --- Demo usage ---
if __name__ == "__main__":
    manager = MultiCameraManager()
    manager.start_all()
    try:
        while True:
            all_frames = manager.get_all_frames()
            for cam_id, data in all_frames.items():
                b64_frame = data["frame"]
                if isinstance(b64_frame, str):
                    # decode for display
                    nparr = np.frombuffer(base64.b64decode(b64_frame), np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                else:
                    frame = b64_frame

                cv2.imshow(f"{cam_id}", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            time.sleep(0.02)
    except KeyboardInterrupt:
        pass
    finally:
        manager.stop_all()
        cv2.destroyAllWindows()
