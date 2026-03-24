# backend/engine/event_engine.py

import time
import random
import logging
import base64
import threading
import cv2

logger = logging.getLogger("event_engine")
logging.basicConfig(level=logging.INFO)

# -----------------------------
# EVENT ENGINE CLASS
# -----------------------------
class EventEngine:
    """
    Demo-ready event engine:
    - Aggregates events per student
    - Simulates AI alerts (multiple faces, looking away, phone detected)
    - Attaches base64 snapshot from MultiCameraManager frame
    - Ready to push to WebSocket frontend
    """

    def __init__(self):
        self.last_events = {}      # student_id -> last event dict
        self.students_frames = {}  # student_id -> latest base64 frame
        self.running = False
        self.lock = threading.Lock()

    # -----------------------------
    # REGISTER FRAME (called by MultiCameraManager)
    # -----------------------------
    def update_frame(self, student_id, b64_frame):
        """Store latest frame for alert snapshots"""
        with self.lock:
            self.students_frames[student_id] = b64_frame

    # -----------------------------
    # START / STOP SIMULATION
    # -----------------------------
    def start_demo_mode(self, student_ids):
        """
        Start background thread to randomly generate alerts for demo
        student_ids: list of student_ids to simulate
        """
        self.running = True
        t = threading.Thread(target=self._simulate_alerts_loop, args=(student_ids,), daemon=True)
        t.start()
        logger.info("[EventEngine] Demo mode started for students")

    def stop_demo_mode(self):
        self.running = False
        logger.info("[EventEngine] Demo mode stopped")

    # -----------------------------
    # SIMULATION LOOP
    # -----------------------------
    def _simulate_alerts_loop(self, student_ids):
        while self.running:
            student_id = random.choice(student_ids)
            timestamp = int(time.time())

            # Random event generation
            event_type, level, message = random.choice([
                ("MULTIPLE_FACES", "HIGH", "Multiple faces detected"),
                ("LOOKING_AWAY", "MEDIUM", "Student looking away"),
                ("PHONE_DETECTED", "HIGH", "Phone detected on desk"),
                ("NO_FACE", "HIGH", "No face detected"),
            ])

            with self.lock:
                snapshot = self.students_frames.get(student_id, None)
                event = {
                    "student_id": student_id,
                    "type": "ALERT",
                    "level": level,
                    "event": message,
                    "timestamp": timestamp,
                    "frame": snapshot
                }
                self.last_events[student_id] = event

            logger.info(f"[EventEngine] Demo Alert: {student_id} | {message}")

            # Sleep 3–8 seconds before next random alert
            time.sleep(random.randint(3, 8))

    # -----------------------------
    # GET ALERTS (for WebSocket)
    # -----------------------------
    def get_latest_alert(self, student_id):
        """Return latest alert for a specific student"""
        with self.lock:
            return self.last_events.get(student_id, None)

    def get_all_alerts(self):
        """Return all latest alerts"""
        with self.lock:
            return self.last_events.copy()

    # -----------------------------
    # PROCESS FRAME (real-time frame analysis)
    # -----------------------------
    def process_frame(self, student_id, frame=None, simulate=True):
        """
        Demo-friendly frame processor:
        - Updates frame in memory
        - Returns simulated analysis results for overlays
        - Includes risk_level and explanation for alert handling
        """
        if frame is not None:
            _, buffer = cv2.imencode(".jpg", frame)
            b64_frame = base64.b64encode(buffer).decode()
            self.update_frame(student_id, b64_frame)

        # Simulated analysis
        faces = random.choice([0, 1, 2])
        gaze = random.choice(["looking_center", "looking_left", "looking_right", "looking_away"])
        objects = random.sample(["cell phone", "book", "calculator"], k=random.randint(0, 2))
        audio_detected = random.random() < 0.3

        # Risk logic
        if faces != 1:
            risk_level = "HIGH"
            explanation = "MULTIPLE_FACES"
        elif gaze == "looking_away":
            risk_level = "MEDIUM"
            explanation = "LOOKING_AWAY"
        elif "cell phone" in objects:
            risk_level = "HIGH"
            explanation = "PHONE_DETECTED"
        else:
            risk_level = "LOW"
            explanation = "NORMAL"

        logger.info(f"[EventEngine] Frame processed: {student_id} | Risk: {risk_level} | Explanation: {explanation}")

        return {
            "student_id": student_id,
            "faces": [{"identity": {"match": True}, "gaze": {"eye_direction": gaze}} for _ in range(faces)],
            "objects_detected": objects,
            "audio_detected": audio_detected,
            "score": random.randint(50, 100),
            "risk_level": risk_level,
            "explanation": explanation
        }

# -----------------------------
# SINGLETON INSTANCE
# -----------------------------
event_engine = EventEngine()

# -----------------------------
# DEMO USAGE
# -----------------------------
if __name__ == "__main__":
    import cv2
    import os

    student_ids = [f"student_{i+1}" for i in range(10)]
    event_engine.start_demo_mode(student_ids)

    demo_path = "services/student_database"
    frame_files = sorted([os.path.join(demo_path, f) for f in os.listdir(demo_path) if f.endswith(".jpg")])
    idx = 0
    try:
        while True:
            for student_id in student_ids:
                if frame_files:
                    frame = cv2.imread(frame_files[idx % len(frame_files)])
                    event_engine.process_frame(student_id, frame)
            idx += 1
            time.sleep(0.5)
    except KeyboardInterrupt:
        event_engine.stop_demo_mode()
        logger.info("Demo stopped")
