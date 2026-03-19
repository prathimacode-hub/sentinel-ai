import os

class Settings:
    # App Config
    APP_NAME = "SentinelAI"
    VERSION = "1.0.0"
    DEBUG = True

    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODEL_DIR = os.path.join(BASE_DIR, "..", "models")
    EVIDENCE_DIR = os.path.join(BASE_DIR, "..", "evidence")

    # Detection Thresholds
    FACE_MISSING_THRESHOLD = 5        # seconds
    GAZE_DEVIATION_THRESHOLD = 3      # seconds

    # Scoring Weights
    SCORE_WEIGHTS = {
        "no_face": 30,
        "multiple_faces": 40,
        "phone_detected": 35,
        "book_detected": 20,
        "looking_away": 10,
        "audio_detected": 20
    }

    # Alert Thresholds
    ALERT_THRESHOLDS = {
        "LOW": 0,
        "MEDIUM": 30,
        "HIGH": 60
    }

    # Security
    HASH_ALGORITHM = "sha256"

settings = Settings()

# Ensure directories exist
os.makedirs(settings.EVIDENCE_DIR, exist_ok=True)
