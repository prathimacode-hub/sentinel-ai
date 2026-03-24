# backend/engine/event_engine.py

import time
import random
import logging
import base64
import threading
import cv2

logger = logging.getLogger("event_engine")
logging.basicConfig(level=logging.INFO)

class EventEngine:
    """
    Event engine for multi-student AI proctoring:
    - Tracks per-student events and latest frames
    - Processes frames for simulated AI alerts
    - Supports HIGH/MEDIUM/LOW risk levels
    - Generates detailed malpractice reports
    """

    def __init__(self):
        self.last_events = {}      # student_id -> last event dict
        self.students_frames = {}  # student_id -> latest base64 frame
        self.student_event_history = {}  # student_id -> list of events
        self.running = False
        self.lock = threading.Lock()

    # -----------------------------
    # FRAME REGISTRATION
    # -----------------------------
    def update_frame(self, student_id, b64_frame):
        """Store latest frame for alerts or snapshots"""
        with self.lock:
            self.students_frames[student_id] = b64_frame

    # -----------------------------
    # SIMULATION CONTROL
    # -----------------------------
    def start_demo_mode(self, student_ids):
        """Start random alert simulation for a list of students"""
        self.running = True
        t = threading.Thread(target=self._simulate_alerts_loop, args=(student_ids,), daemon=True)
        t.start()
        logger.info(f"[EventEngine] Demo mode started for {len(student_ids)} students")

    def stop_demo_mode(self):
        self.running = False
        logger.info("[EventEngine] Demo mode stopped")

    # -----------------------------
    # RANDOM ALERT LOOP (SIMULATION)
    # -----------------------------
    def _simulate_alerts_loop(self, student_ids):
        while self.running:
            student_id = random.choice(student_ids)
            timestamp = int(time.time())
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
                self.student_event_history.setdefault(student_id, []).append(event)

            logger.info(f"[EventEngine] Demo Alert: {student_id} | {message}")
            time.sleep(random.randint(3, 8))

    # -----------------------------
    # ALERT RETRIEVAL
    # -----------------------------
    def get_latest_alert(self, student_id):
        """Get latest alert for a specific student"""
        with self.lock:
            return self.last_events.get(student_id)

    def get_all_alerts(self):
        """Get latest alerts for all students"""
        with self.lock:
            return self.last_events.copy()

    # -----------------------------
    # PROCESS FRAME (REAL-TIME)
    # -----------------------------
    def process_frame(self, student_id, frame=None, simulate=True):
        """
        Process a frame:
        - Updates latest base64 frame
        - Returns a risk assessment with explanation
        - Saves event history
        """
        if frame is not None:
            _, buffer = cv2.imencode(".jpg", frame)
            b64_frame = base64.b64encode(buffer).decode()
            self.update_frame(student_id, b64_frame)

        # Simulated detection
        faces = random.choice([0, 1, 2])
        gaze = random.choice(["looking_center", "looking_left", "looking_right", "looking_away"])
        objects = random.sample(["cell phone", "book", "calculator"], k=random.randint(0, 2))
        audio_detected = random.random() < 0.3

        # Determine risk level
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

        timestamp = int(time.time())
        event = {
            "student_id": student_id,
            "type": "ALERT",
            "level": risk_level,
            "event": explanation,
            "timestamp": timestamp,
            "frame": self.students_frames.get(student_id)
        }

        with self.lock:
            self.last_events[student_id] = event
            self.student_event_history.setdefault(student_id, []).append(event)

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
    # STUDENT MALPRACTICE REPORT
    # -----------------------------
    def generate_malpractice_report(self):
        """
        Returns a full report of all students with events, timestamps, risk levels, and explanations
        """
        with self.lock:
            report = {}
            for student_id, events in self.student_event_history.items():
                report[student_id] = [
                    {
                        "timestamp": e["timestamp"],
                        "risk_level": e["level"],
                        "explanation": e["event"]
                    }
                    for e in events
                ]
            return report


# -----------------------------
# SINGLETON INSTANCE
# -----------------------------
event_engine = EventEngine()
