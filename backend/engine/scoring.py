# backend/engine/scoring.py
# Sentinel-AI scoring module
# Calculates risk scores for exam behaviors (identity, gaze, objects, audio)

# -----------------------------
# SAFE CONFIG IMPORT
# -----------------------------
try:
    from config import settings
    WEIGHTS = settings.SCORE_WEIGHTS
except Exception:
    print("⚠ Using default scoring weights")
    WEIGHTS = {
        "multiple_faces": 30,
        "no_face": 25,
        "looking_away": 15,
        "phone_detected": 25,
        "book_detected": 20,
        "audio_detected": 15,
        "obstruction": 20,
        "impersonation": 40
    }


# -----------------------------
# MAIN SCORING FUNCTION
# -----------------------------
def calculate_score(events: list):
    """
    Calculate cheating/exam risk score based on detected events.

    Args:
        events (list): List of event dicts from event_engine.
    Returns:
        dict: {
            total_score: int,
            breakdown: dict,
            risk_level: str
        }
    """

    score = 0
    breakdown = {}

    # -----------------------------
    # MAP EVENTS TO SCORING KEYS
    # -----------------------------
    behavior_map = {
        "MULTIPLE_FACES": "multiple_faces",
        "NO_FACE": "no_face",
        "LOOKING_AWAY": "looking_away",
        "PHONE_USAGE": "phone_detected",
        "BOOK_USAGE": "book_detected",
        "VOICE_DETECTED": "audio_detected",
        "CAMERA_BLOCKED": "obstruction",
        "IMPERSONATION": "impersonation"
    }

    behavior_flags = {}

    for e in events:
        # -----------------------------
        # SAFE CHECK: ensure e is dict
        # -----------------------------
        if not isinstance(e, dict):
            continue  # skip invalid entries

        key = behavior_map.get(e.get("type"))
        if key:
            behavior_flags[key] = True
            score += WEIGHTS.get(key, 0)
            breakdown[key] = WEIGHTS.get(key, 0)

    # -----------------------------
    # ADVANCED COMBINATIONS / SMART BONUSES
    # -----------------------------
    if behavior_flags.get("multiple_faces") and behavior_flags.get("audio_detected"):
        bonus = 15
        score += bonus
        breakdown["collaboration_bonus"] = bonus

    if behavior_flags.get("phone_detected") and behavior_flags.get("looking_away"):
        bonus = 10
        score += bonus
        breakdown["phone_usage_suspicion"] = bonus

    if behavior_flags.get("no_face") and behavior_flags.get("audio_detected"):
        bonus = 20
        score += bonus
        breakdown["hidden_user_audio"] = bonus

    if behavior_flags.get("impersonation"):
        bonus = 20
        score += bonus
        breakdown["identity_violation"] = bonus

    if behavior_flags.get("obstruction") and behavior_flags.get("no_face"):
        bonus = 10
        score += bonus
        breakdown["camera_blocked"] = bonus

    # -----------------------------
    # NORMALIZE SCORE
    # -----------------------------
    total_score = min(score, 100)

    # -----------------------------
    # RISK LEVEL
    # -----------------------------
    if total_score >= 70:
        risk_level = "HIGH"
    elif total_score >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "total_score": total_score,
        "breakdown": breakdown,
        "risk_level": risk_level
    }


# -----------------------------
# QUICK DEMO
# -----------------------------
if __name__ == "__main__":
    # Example usage
    sample_events = [
        {"type": "NO_FACE", "level": "HIGH"},
        {"type": "LOOKING_AWAY", "level": "MEDIUM"},
        {"type": "PHONE_USAGE", "level": "HIGH"},
    ]
    result = calculate_score(sample_events)
    print("Score Result:", result)
