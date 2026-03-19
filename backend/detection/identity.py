import face_recognition
import numpy as np
from typing import Dict


class IdentityVerifier:
    def __init__(self):
        self.known_encodings = {}
        self.threshold = 0.5  # lower = stricter

    def register_student(self, student_id: str, image):
        """
        Register a student's face encoding
        """
        encodings = face_recognition.face_encodings(image)

        if not encodings:
            return {"status": "failed", "reason": "No face found"}

        self.known_encodings[student_id] = encodings[0]

        return {"status": "registered", "student_id": student_id}

    def verify(self, student_id: str, frame) -> Dict:
        """
        Verify if current face matches registered student
        """
        if student_id not in self.known_encodings:
            return {"match": False, "reason": "Student not registered"}

        known_encoding = self.known_encodings[student_id]

        face_locations = face_recognition.face_locations(frame)
        encodings = face_recognition.face_encodings(frame, face_locations)

        if not encodings:
            return {"match": False, "reason": "No face detected"}

        distances = face_recognition.face_distance([known_encoding], encodings[0])
        match = distances[0] < self.threshold

        return {
            "match": bool(match),
            "distance": float(distances[0]),
            "faces_detected": len(encodings)
        }


# -----------------------------
# GLOBAL INSTANCE
# -----------------------------
identity_verifier = IdentityVerifier()
