# backend/detection/identity.py
# Sentinel-AI - Identity Verification Module (Corrected)
# Production-ready DeepFace-only, simulation supported

import random
import cv2
import os
from deepface import DeepFace

# -----------------------------
# PATHS
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDENT_DB_DIR = os.path.join(BASE_DIR, "student_database")

# -----------------------------
# IDENTITY VERIFIER CLASS
# -----------------------------
class IdentityVerifier:

    def __init__(self):
        print("🧠 Identity running in DeepFace-only mode")

    # -----------------------------
    # GET STUDENT IMAGE
    # -----------------------------
    def get_student_image(self, student_id):
        img_path = os.path.join(STUDENT_DB_DIR, f"{student_id}.jpg")
        return img_path if os.path.exists(img_path) else None

    # -----------------------------
    # VERIFY
    # -----------------------------
    def verify(self, frame=None, student_id=None, simulate=False):
        """
        Returns list of behavior flags:
        [
            {"type": "identity_verified", "value": True/False},
            {"type": "faces_detected", "value": n}
        ]
        """
        flags = []

        # -----------------------------
        # SIMULATION MODE
        # -----------------------------
        if simulate:
            choice = random.choice([
                "NO_FACE", "ONE_FACE", "MULTIPLE_FACES", "IMPERSONATION"
            ])

            if choice == "NO_FACE":
                flags.append({"type": "faces_detected", "value": 0})
                flags.append({"type": "identity_verified", "value": False})
                return flags

            elif choice == "ONE_FACE":
                flags.append({"type": "faces_detected", "value": 1})
                flags.append({"type": "identity_verified", "value": True})
                return flags

            elif choice == "MULTIPLE_FACES":
                flags.append({"type": "faces_detected", "value": 2})
                flags.append({"type": "identity_verified", "value": False})
                return flags

            else:  # IMPERSONATION
                flags.append({"type": "faces_detected", "value": 1})
                flags.append({"type": "identity_verified", "value": False})
                return flags

        # -----------------------------
        # NO FRAME PROVIDED
        # -----------------------------
        if frame is None:
            flags.append({"type": "faces_detected", "value": 0})
            flags.append({"type": "identity_verified", "value": False})
            return flags

        # -----------------------------
        # DEEPFACE VERIFICATION
        # -----------------------------
        if student_id:
            try:
                reference_img = self.get_student_image(student_id)
                if reference_img is None:
                    flags.append({"type": "faces_detected", "value": 0})
                    flags.append({"type": "identity_verified", "value": False})
                    return flags

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                result = DeepFace.verify(
                    img1_path=rgb_frame,
                    img2_path=reference_img,
                    model_name="Facenet",
                    detector_backend="opencv",
                    enforce_detection=False
                )

                verified = result.get("verified", False)
                distance = result.get("distance", 1.0)

                flags.append({"type": "faces_detected", "value": 1})
                flags.append({"type": "identity_verified", "value": verified})
                return flags

            except Exception as e:
                print("⚠ DeepFace error:", e)
                flags.append({"type": "faces_detected", "value": 0})
                flags.append({"type": "identity_verified", "value": False})
                return flags

        # -----------------------------
        # DEFAULT FALLBACK (no student_id)
        # -----------------------------
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = DeepFace.extract_faces(
                img_path=rgb_frame,
                detector_backend="opencv",
                enforce_detection=False
            )
            face_count = len(faces)

            flags.append({"type": "faces_detected", "value": face_count})
            flags.append({"type": "identity_verified", "value": face_count == 1})
            return flags

        except Exception as e:
            print("⚠ Identity verification error:", e)
            flags.append({"type": "faces_detected", "value": 0})
            flags.append({"type": "identity_verified", "value": False})
            return flags

# -----------------------------
# SINGLETON INSTANCE
# -----------------------------
identity_verifier = IdentityVerifier()

# -----------------------------
# BACKWARD COMPATIBILITY
# -----------------------------
def verify_identity(frame=None, student_id=None, simulate=False):
    return identity_verifier.verify(frame=frame, student_id=student_id, simulate=simulate)
