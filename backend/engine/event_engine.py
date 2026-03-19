from config import settings
import datetime

def generate_event(score_data: dict, behavior: dict):
    """
    Generate event level, explanation, and metadata
    """

    score = score_data["total_score"]

    thresholds = settings.ALERT_THRESHOLDS

    # -----------------------------
    # DETERMINE LEVEL
    # -----------------------------
    if score >= thresholds["HIGH"]:
        level = "HIGH"
    elif score >= thresholds["MEDIUM"]:
        level = "MEDIUM"
    else:
        level = "LOW"

    # -----------------------------
    # GENERATE EXPLANATION (XAI)
    # -----------------------------
    reasons = []

    for key, value in behavior.items():
        if value is True:
            reasons.append(key)

    explanation = generate_explanation(reasons)

    # -----------------------------
    # TIMESTAMP
    # -----------------------------
    timestamp = datetime.datetime.utcnow().isoformat()

    return {
        "level": level,
        "score": score,
        "timestamp": timestamp,
        "reasons": reasons,
        "explanation": explanation
    }


def generate_explanation(reasons: list):
    """
    Convert raw flags into human-readable explanation
    """

    explanation_map = {
        "no_face": "Student not visible in camera",
        "multiple_faces": "Multiple people detected",
        "phone_detected": "Mobile phone detected",
        "book_detected": "Book or notes detected",
        "looking_away": "Student frequently looking away",
        "audio_detected": "Speech detected in background",
        "possible_collaboration": "Possible collaboration detected",
        "attention_loss": "Student not focused on screen"
    }

    explanations = []

    for r in reasons:
        if r in explanation_map:
            explanations.append(explanation_map[r])

    if not explanations:
        return "No suspicious activity"

    return "; ".join(explanations)
