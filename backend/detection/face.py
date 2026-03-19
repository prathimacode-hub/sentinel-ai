import cv2
import numpy as np

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

def detect_face(frame):
    """
    Detect faces in the frame
    Returns:
        face_count
        face_locations
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(30, 30)
    )

    face_list = []
    for (x, y, w, h) in faces:
        face_list.append({
            "x": int(x),
            "y": int(y),
            "w": int(w),
            "h": int(h)
        })

    return {
        "face_count": len(face_list),
        "faces": face_list
    }
