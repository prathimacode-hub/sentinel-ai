from config import settings

def calculate_score(behavior: dict):
    """
    Assign weighted score to behaviors
    """

    score = 0
    breakdown = {}

    weights = settings.SCORE_WEIGHTS

    for key, weight in weights.items():
        if behavior.get(key, False):
            score += weight
            breakdown[key] = weight

    # -----------------------------
    # BONUS PENALTIES (SMART EDGE)
    # -----------------------------
    # Combine behaviors for stronger signals

    if behavior.get("multiple_faces") and behavior.get("audio_detected"):
        score += 15
        breakdown["collaboration_bonus"] = 15

    if behavior.get("phone_detected") and behavior.get("looking_away"):
        score += 10
        breakdown["phone_usage_suspicion"] = 10

    if behavior.get("no_face") and behavior.get("audio_detected"):
        score += 20
        breakdown["hidden_user_audio"] = 20

    # Cap score at 100
    score = min(score, 100)

    return {
        "total_score": score,
        "breakdown": breakdown
    }
