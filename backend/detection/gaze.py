# backend/detection/gaze.py
# Sentinel-AI - Gaze Detection Module (Corrected)

import cv2
import numpy as np
from deepface import DeepFace
from math import atan2, degrees
import random

class GazeDetector:
    def __init__(self, simulation_mode=False):
        self.detector_backend = 'opencv'  # DeepFace backend
        self.simulation_mode = simulation_mode

    # -----------------------------
    # FACE DETECTION
    # -----------------------------
    def detect_faces(self, frame):
        """Detect faces using DeepFace."""
        try:
            detections = DeepFace.extract_faces(
                frame,
                detector_backend=self.detector_backend,
                enforce_detection=False
            )
            return detections
        except Exception as e:
            print("⚠ Face detection error:", e)
            return []

    # -----------------------------
    # HEAD POSE
    # -----------------------------
    def get_head_pose(self, landmarks, frame_shape):
        """Compute head pose from facial landmarks."""
        required_keys = ['nose', 'chin', 'left_eye_corner', 'right_eye_corner', 'mouth_left', 'mouth_right']
        if not all(landmarks.get(k) is not None for k in required_keys):
            return np.array([0.0, 0.0, 0.0])

        model_points = np.array([
            (0.0, 0.0, 0.0),
            (0.0, -330.0, -65.0),
            (-225.0, 170.0, -135.0),
            (225.0, 170.0, -135.0),
            (-150.0, -150.0, -125.0),
            (150.0, -150.0, -125.0)
        ], dtype=np.float64)

        image_points = np.array([
            landmarks['nose'],
            landmarks['chin'],
            landmarks['left_eye_corner'],
            landmarks['right_eye_corner'],
            landmarks['mouth_left'],
            landmarks['mouth_right']
        ], dtype=np.float64)

        size = (frame_shape[1], frame_shape[0])
        focal_length = size[1]
        center = (size[1]/2, size[0]/2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype="double")
        dist_coeffs = np.zeros((4, 1))

        try:
            success, rotation_vector, translation_vector = cv2.solvePnP(
                model_points, image_points, camera_matrix, dist_coeffs
            )
            rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
            sy = np.sqrt(rotation_matrix[0,0]**2 + rotation_matrix[1,0]**2)
            pitch = atan2(-rotation_matrix[2,0], sy)
            yaw = atan2(rotation_matrix[1,0], rotation_matrix[0,0])
            roll = atan2(rotation_matrix[2,1], rotation_matrix[2,2])
            return np.array([degrees(pitch), degrees(yaw), degrees(roll)])
        except:
            return np.array([0.0, 0.0, 0.0])

    # -----------------------------
    # GAZE DIRECTION
    # -----------------------------
    def get_eye_direction(self, landmarks, head_pose):
        """Compute gaze direction: left, right, center, away."""
        left_eye = landmarks.get('left_eye')
        right_eye = landmarks.get('right_eye')
        if left_eye is None or right_eye is None:
            return "unknown"

        dx = right_eye[0] - left_eye[0]
        dy = right_eye[1] - left_eye[1]
        angle = degrees(atan2(dy, dx))
        yaw = head_pose[1]

        if abs(yaw) > 25:
            return "looking_away"
        elif angle < -10 or yaw < -10:
            return "looking_left"
        elif angle > 10 or yaw > 10:
            return "looking_right"
        else:
            return "looking_center"

    # -----------------------------
    # SIMULATION MODE
    # -----------------------------
    def simulate_face(self, frame, idx=0):
        """Simulate a face with random gaze direction."""
        h, w = frame.shape[:2]
        x1, y1 = 50 + idx*20, 50 + idx*20
        x2, y2 = x1 + 100, y1 + 100
        directions = ["looking_center", "looking_left", "looking_right", "looking_away"]
        eye_dir = random.choice(directions)
        return {
            "bbox": [x1, y1, x2, y2],
            "head_pose": [0, 0, 0],
            "gaze": [{"type": "eye_direction", "value": eye_dir}]
        }

    # -----------------------------
    # PROCESS FRAME
    # -----------------------------
    def process_frame(self, frame):
        """Process a frame and return list of faces with gaze info."""
        results = []

        if self.simulation_mode:
            for i in range(random.randint(1,3)):
                results.append(self.simulate_face(frame, i))
            return results

        detections = self.detect_faces(frame)

        for face in detections:
            keypoints = face.get('facial_area', {})

            def safe_point(name):
                kp = keypoints.get(name)
                if kp is not None and 'x' in kp and 'y' in kp:
                    return (kp['x'], kp['y'])
                return None

            landmarks = {
                'nose': safe_point('nose'),
                'chin': safe_point('chin'),
                'left_eye_corner': safe_point('left_eye'),
                'right_eye_corner': safe_point('right_eye'),
                'mouth_left': safe_point('mouth_left'),
                'mouth_right': safe_point('mouth_right'),
                'left_eye': safe_point('left_eye'),
                'right_eye': safe_point('right_eye')
            }

            bbox = face.get('facial_area', {}).get('bbox', [50,50,150,150])
            head_pose = self.get_head_pose(landmarks, frame.shape)
            eye_direction = self.get_eye_direction(landmarks, head_pose)

            # ✅ Always return gaze as list of dicts
            gaze_flags = [{"type": "eye_direction", "value": eye_direction}]

            results.append({
                "bbox": bbox,
                "head_pose": head_pose.tolist(),
                "gaze": gaze_flags
            })

        return results

    # -----------------------------
    # PLACEHOLDER: AUDIO & OBJECTS
    # -----------------------------
    def detect_audio(self, frame):
        return random.choice([True, False])

    def detect_objects(self, frame):
        sample_objects = ["cell phone", "book", "pen", "laptop"]
        count = random.randint(0, 2)
        return random.sample(sample_objects, count)

# -----------------------------
# SINGLETON INSTANCE
# -----------------------------
gaze_detector = GazeDetector(simulation_mode=True)
