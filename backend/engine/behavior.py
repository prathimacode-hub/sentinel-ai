# backend/engine/behavior.py
# Sentinel-AI behavior analysis module
# Converts raw detection outputs into structured behavior signals

from typing import Dict

def analyze_behavior(face_data: Dict, object_data: Dict, gaze_data: Dict, audio_data: Dict) -> Dict:
    """
    Convert raw detection outputs into structured behavior signals.

    Args:
        face_data (dict): Output from identity_verifier / face engine
            Expected keys: face_count, identity -> {match: bool}
        object_data (dict): Output from object detector
            Expected keys: objects (list), obstruction (bool)
        gaze_data (dict): Output from gaze_detector
            Expected keys: eye_direction
        audio_data (dict): Output from audio detector
            Expected keys: speech_detected (bool)

    Returns:
        dict: behavior signals for scoring
    """

    behavior = {}

    # -----------------------------
    # FACE-BASED BEHAVIOR
    # -----------------------------
    face_count = face_data.get("faces_detected", 0)
    verified = face_data.get("verified", True)

    behavior["no_face"] = face_count == 0
    behavior["multiple_faces"] = face_count > 1
    behavior["single_face"] = face_count == 1

    # Impersonation based on identity match
    behavior["impersonation"] = not verified

    # -----------------------------
    # OBJECT-BASED BEHAVIOR
    # -----------------------------
    objects = object_data.get("objects", [])
    obstruction = object_data.get("obstruction", False)

    behavior["phone_detected"] = "cell phone" in objects
    behavior["book_detected"] = "book" in objects
    behavior["laptop_detected"] = "laptop" in objects
    behavior["camera_blocked"] = obstruction

    # -----------------------------
    # GAZE BEHAVIOR
    # -----------------------------
    eye_direction = gaze_data.get("eye_direction", "unknown")
    behavior["looking_away"] = eye_direction == "looking_away"

    # -----------------------------
    # AUDIO BEHAVIOR
    # -----------------------------
    speech = audio_data.get("speech_detected", False)
    behavior["audio_detected"] = speech

    # -----------------------------
    # DERIVED / ADVANCED FLAGS
    # -----------------------------
    # Any suspicious object usage
    behavior["suspicious_object"] = behavior["phone_detected"] or behavior["book_detected"] or behavior["laptop_detected"]

    # Attention loss: looking away + speech
    behavior["attention_loss"] = behavior["looking_away"] and behavior["audio_detected"]

    # Possible collaboration: multiple faces or speech detected
    behavior["possible_collaboration"] = behavior["multiple_faces"] or behavior["audio_detected"]

    return behavior


# -----------------------------
# QUICK DEMO
# -----------------------------
if __name__ == "__main__":
    # Example test
    face_data = {"faces_detected": 2, "verified": False}
    object_data = {"objects": ["cell phone", "book"], "obstruction": True}
    gaze_data = {"eye_direction": "looking_away"}
    audio_data = {"speech_detected": True}

    result = analyze_behavior(face_data, object_data, gaze_data, audio_data)
    print("Behavior Analysis Result:")
    for k, v in result.items():
        print(f"  {k}: {v}")
