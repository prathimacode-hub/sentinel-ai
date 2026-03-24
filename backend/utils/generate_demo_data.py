# backend/utils/generate_demo_data.py

import os
import json
import cv2
import numpy as np

# -----------------------------
# CONFIG
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STUDENT_DB_DIR = os.path.join(BASE_DIR, "student_database")
CONFIG_DIR = os.path.join(BASE_DIR, "services")
CAMERA_REGISTRY_PATH = os.path.join(CONFIG_DIR, "camera_registry.json")

TOTAL_STUDENTS = 30

os.makedirs(STUDENT_DB_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# -----------------------------
# CREATE STUDENT IMAGES
# -----------------------------
def create_student_images():

    print("Creating student images...")

    for i in range(1, TOTAL_STUDENTS + 1):

        student_id = f"student_{i}"

        image = np.ones((480, 640, 3), dtype=np.uint8) * 255

        # Draw face
        cv2.circle(image, (320, 200), 80, (0, 0, 0), 3)

        # Eyes
        cv2.circle(image, (290, 180), 10, (0, 0, 0), -1)
        cv2.circle(image, (350, 180), 10, (0, 0, 0), -1)

        # Mouth
        cv2.ellipse(image, (320, 230), (30, 15), 0, 0, 180, (0, 0, 0), 2)

        # Text
        cv2.putText(
            image,
            student_id,
            (200, 350),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2,
            cv2.LINE_AA
        )

        path = os.path.join(STUDENT_DB_DIR, f"{student_id}.jpg")

        cv2.imwrite(path, image)

    print("Student images created successfully")


# -----------------------------
# CREATE CAMERA REGISTRY
# -----------------------------
def create_camera_registry():

    print("Creating camera registry...")

    registry = {
        "students": [],
        "hall_cctv": []
    }

    for i in range(1, TOTAL_STUDENTS + 1):

        student_entry = {

            "student_id": f"student_{i}",
            "camera_id": f"cam_{i}",

            # Demo webcam / RTSP simulation
            "rtsp_url": 0 if i == 1 else f"rtsp://192.168.1.{100+i}/stream"
        }

        registry["students"].append(student_entry)

    # Hall CCTV
    registry["hall_cctv"].append({

        "camera_id": "hall_cam_1",
        "rtsp_url": "rtsp://192.168.1.200/stream"
    })

    with open(CAMERA_REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=4)

    print("Camera registry created")


# -----------------------------
# SUMMARY
# -----------------------------
def summary():

    print("\nDemo Data Generated Successfully\n")

    print("Student Database:")
    print(STUDENT_DB_DIR)

    print("\nCamera Registry:")
    print(CAMERA_REGISTRY_PATH)

    print("\nTotal Students:", TOTAL_STUDENTS)
    print("Hall CCTV: 1")

    print("\nSystem Ready for Demo")


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":

    create_student_images()
    create_camera_registry()
    summary()
