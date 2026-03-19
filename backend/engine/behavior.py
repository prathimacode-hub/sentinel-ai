from typing import Dict

def analyze_behavior(face_data: Dict, object_data: Dict, gaze_data: Dict, audio_data: Dict):
    """
    Convert raw detection outputs into structured behavior signals
    """

    behavior = {}

    # -----------------------------
    # FACE-BASED BEHAVIOR
    # -----------------------------
    face_count = face_data.get("face_count", 0)

    behavior["no_face"] = face_count == 0
    behavior["multiple_faces"] = face_count > 1
    behavior["single_face"] = face_count == 1

    # -----------------------------
    # OBJECT-BASED BEHAVIOR
    # -----------------------------
    objects = object_data.get("objects", [])

    behavior["phone_detected"] = "cell phone" in objects
    behavior["book_detected"] = "book" in objects
    behavior["laptop_detected"] = "laptop" in objects

    # -----------------------------
    # GAZE BEHAVIOR
    # -----------------------------
    behavior["looking_away"] = gaze_data.get("looking_away", False)

    # -----------------------------
    # AUDIO BEHAVIOR
    # -----------------------------
    behavior["audio_detected"] = audio_data.get("speech_detected", False)

    # -----------------------------
    # ADVANCED FLAGS (Derived)
    # -----------------------------
    behavior["suspicious_object"] = (
        behavior["phone_detected"] or behavior["book_detected"]
    )

    behavior["attention_loss"] = (
        behavior["looking_away"] and behavior["audio_detected"]
    )

    # add this inside analyze_behavior()

    identity_data = face_data.get("identity", {})

    behavior["impersonation"] = not identity_data.get("match", True)

    behavior["possible_collaboration"] = (
        behavior["multiple_faces"] or behavior["audio_detected"]
    )

    return behavior
