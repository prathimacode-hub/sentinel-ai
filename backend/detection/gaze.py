import cv2
import mediapipe as mp
import numpy as np

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False)

def detect_gaze(frame):
    """
    Detect if user is looking away using head pose approximation
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    looking_away = False

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Nose tip landmark
            nose = face_landmarks.landmark[1]

            # Check deviation
            if nose.x < 0.3 or nose.x > 0.7:
                looking_away = True

    return {
        "looking_away": looking_away
    }
