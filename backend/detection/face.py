# detection/face.py

import cv2
import numpy as np
import random
import logging

logger = logging.getLogger("SentinelAI.Face")

# -----------------------------
# TRY DEEPFACE
# -----------------------------
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
    logger.info("DeepFace loaded successfully")
except Exception as e:
    logger.warning(f"DeepFace not available: {e}")
    DEEPFACE_AVAILABLE = False

# -----------------------------
# HAAR CASCADE FALLBACK
# -----------------------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# -----------------------------
# FACE DETECTION FUNCTION
# -----------------------------
def detect_face(frame, simulate=False):
    """
    Detect faces in the frame

    Returns:
        {
            face_count: int
            faces: list
            mode: str
        }
    """

    # -----------------------------
    # SIMULATION MODE
    # -----------------------------
    if simulate:

        choice = random.choice(
            ["NO_FACE", "ONE_FACE", "MULTIPLE_FACES"]
        )

        if choice == "NO_FACE":
            return {
                "face_count": 0,
                "faces": [],
                "mode": "simulated"
            }

        elif choice == "ONE_FACE":
            return {
                "face_count": 1,
                "faces": [
                    {"x": 120, "y": 100, "w": 90, "h": 90}
                ],
                "mode": "simulated"
            }

        else:
            return {
                "face_count": 2,
                "faces": [
                    {"x": 60, "y": 80, "w": 85, "h": 85},
                    {"x": 180, "y": 90, "w": 80, "h": 80}
                ],
                "mode": "simulated"
            }

    # -----------------------------
    # REAL DETECTION
    # -----------------------------
    faces_list = []

    try:

        # -----------------------------
        # DEEPFACE DETECTION
        # -----------------------------
        if DEEPFACE_AVAILABLE:

            detections = DeepFace.extract_faces(
                img_path=frame,
                detector_backend="opencv",
                enforce_detection=False
            )

            for face in detections:

                region = face.get("facial_area", {})

                x = region.get("x", 0)
                y = region.get("y", 0)
                w = region.get("w", 0)
                h = region.get("h", 0)

                if w > 0 and h > 0:
                    faces_list.append({
                        "x": int(x),
                        "y": int(y),
                        "w": int(w),
                        "h": int(h)
                    })

            mode_used = "deepface"

        else:

            # -----------------------------
            # HAAR CASCADE FALLBACK
            # -----------------------------
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            detected = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=5,
                minSize=(30, 30)
            )

            for (x, y, w, h) in detected:
                faces_list.append({
                    "x": int(x),
                    "y": int(y),
                    "w": int(w),
                    "h": int(h)
                })

            mode_used = "haar_cascade"

    except Exception as e:

        logger.error(f"Face detection error: {e}")

        return {
            "face_count": 0,
            "faces": [],
            "mode": "error"
        }

    return {
        "face_count": len(faces_list),
        "faces": faces_list,
        "mode": mode_used
    }

# -----------------------------
# DRAW FACES
# -----------------------------
def draw_faces(frame, faces):
    """
    Draw bounding boxes on faces
    """

    for f in faces:

        x = f["x"]
        y = f["y"]
        w = f["w"]
        h = f["h"]

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "Face",
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )

    return frame
