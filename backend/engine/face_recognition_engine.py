# backend/engine/face_recognition_engine.py

import os
import cv2
import numpy as np
import logging
from deepface import DeepFace

logger = logging.getLogger("SentinelAI.FaceRecognition")

# -----------------------------
# CONFIGURATION
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDENT_DB_DIR = os.path.join(BASE_DIR, "student_database")

FACIAL_BACKEND = "Facenet"
DETECTION_MODEL = "opencv"
VERIFY_THRESHOLD = 0.35

# -----------------------------
# DATABASE CACHE
# -----------------------------
STUDENT_IMAGES = {}
STUDENT_EMBEDDINGS = {}

# -----------------------------
# LOAD STUDENT IMAGES
# -----------------------------
def load_student_images():
    """
    Load all student images from database
    """
    student_images = {}

    if not os.path.exists(STUDENT_DB_DIR):
        os.makedirs(STUDENT_DB_DIR)

    for filename in os.listdir(STUDENT_DB_DIR):

        if filename.lower().endswith((".jpg", ".png", ".jpeg")):

            student_id = os.path.splitext(filename)[0]
            path = os.path.join(STUDENT_DB_DIR, filename)

            student_images[student_id] = path

    return student_images


# -----------------------------
# PRELOAD DATABASE
# -----------------------------
def preload_student_database():

    global STUDENT_IMAGES
    global STUDENT_EMBEDDINGS

    STUDENT_IMAGES = load_student_images()

    logger.info(f"Loaded {len(STUDENT_IMAGES)} students")

    for student_id, img_path in STUDENT_IMAGES.items():

        try:

            embedding = DeepFace.represent(
                img_path=img_path,
                model_name=FACIAL_BACKEND,
                detector_backend=DETECTION_MODEL,
                enforce_detection=False
            )

            if embedding and len(embedding) > 0:
                STUDENT_EMBEDDINGS[student_id] = embedding[0]["embedding"]

        except Exception as e:
            logger.warning(f"Failed to load embedding for {student_id}: {e}")


# preload at start
preload_student_database()

# -----------------------------
# NORMALIZE CONFIDENCE
# -----------------------------
def distance_to_confidence(distance):

    confidence = max(0, min(1, 1 - distance))
    return round(confidence * 100, 2)


# -----------------------------
# FACE RECOGNITION
# -----------------------------
def recognize_face(frame, student_id, simulate=False):

    """
    Verify student identity

    Returns:
    {
        verified: bool
        confidence: float
        distance: float
        message: str
    }
    """

    # -----------------------------
    # SIMULATION MODE
    # -----------------------------
    if simulate:

        import random

        result = random.choice(
            [
                (True, 0.12, "Face verified"),
                (False, 0.55, "Unknown person detected"),
                (False, 0.90, "No face detected"),
            ]
        )

        return {
            "verified": result[0],
            "confidence": distance_to_confidence(result[1]),
            "distance": result[1],
            "message": result[2],
            "mode": "simulated"
        }

    # -----------------------------
    # STUDENT EXISTS
    # -----------------------------
    if student_id not in STUDENT_IMAGES:

        return {
            "verified": False,
            "confidence": 0,
            "distance": 1.0,
            "message": f"No registered image for {student_id}",
            "mode": "error"
        }

    reference_img_path = STUDENT_IMAGES[student_id]

    try:

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = DeepFace.verify(
            img1_path=rgb_frame,
            img2_path=reference_img_path,
            model_name=FACIAL_BACKEND,
            detector_backend=DETECTION_MODEL,
            enforce_detection=False
        )

        distance = float(result.get("distance", 1.0))
        verified = result.get("verified", False)

        confidence = distance_to_confidence(distance)

        if verified:
            message = "Student identity verified"
        else:
            message = "Identity mismatch"

        return {
            "verified": verified,
            "confidence": confidence,
            "distance": distance,
            "message": message,
            "mode": "deepface"
        }

    except Exception as e:

        logger.error(f"Recognition error: {e}")

        return {
            "verified": False,
            "confidence": 0,
            "distance": 1.0,
            "message": f"Recognition failed: {str(e)}",
            "mode": "error"
        }


# -----------------------------
# RELOAD DATABASE
# -----------------------------
def reload_database():

    STUDENT_IMAGES.clear()
    STUDENT_EMBEDDINGS.clear()

    preload_student_database()

    return {
        "status": "reloaded",
        "students": len(STUDENT_IMAGES)
    }


# -----------------------------
# GET REGISTERED STUDENTS
# -----------------------------
def get_registered_students():

    return list(STUDENT_IMAGES.keys())


# -----------------------------
# TEST MODE
# -----------------------------
if __name__ == "__main__":

    print("Testing Face Recognition Engine")

    test_image_path = os.path.join(
        STUDENT_DB_DIR,
        "student_1.jpg"
    )

    if os.path.exists(test_image_path):

        frame = cv2.imread(test_image_path)

        result = recognize_face(
            frame,
            "student_1"
        )

        print(result)

    else:
        print("No student_1 image found")
