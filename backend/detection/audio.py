# backend/detection/audio.py
# Sentinel-AI - Audio Detection Module
# Production-ready, returns list of behavior flags for scoring

import random

# -----------------------------
# SAFE IMPORT (OPTIONAL LIBRARY)
# -----------------------------
try:
    import webrtcvad

    VAD_AVAILABLE = True
    vad = webrtcvad.Vad()
    vad.set_mode(2)  # 0–3 (higher = stricter)

except ImportError:
    print("⚠ webrtcvad not installed → using simulation mode")
    VAD_AVAILABLE = False
    vad = None

# -----------------------------
# HELPER: SIMULATION LOGIC
# -----------------------------
def _simulate_audio(mode="default"):
    """
    Generate realistic simulated audio detection as a list of dicts
    """
    speech = random.choice([True, False])
    return [{
        "type": "audio_alert",
        "value": speech,
        "confidence": round(random.uniform(0.6, 0.95), 2),
        "mode": "simulated" if mode=="default" else "simulated_no_audio"
    }]

# -----------------------------
# MAIN AUDIO DETECTION
# -----------------------------
def detect_audio(audio_bytes=None, sample_rate=16000):
    """
    Audio detection using:
    - webrtcvad (if available)
    - fallback simulation (if not)

    Returns:
        list of dicts: [{"type": "audio_alert", "value": bool, "confidence": float, "mode": str}]
    """

    # -----------------------------
    # CASE 1: VAD NOT AVAILABLE
    # -----------------------------
    if not VAD_AVAILABLE:
        return _simulate_audio()

    # -----------------------------
    # CASE 2: NO AUDIO INPUT
    # -----------------------------
    if audio_bytes is None:
        return _simulate_audio(mode="no_audio")

    # -----------------------------
    # CASE 3: REAL AUDIO DETECTION
    # -----------------------------
    try:
        is_speech = vad.is_speech(audio_bytes, sample_rate)

        return [{
            "type": "audio_alert",
            "value": bool(is_speech),
            "confidence": 0.9 if is_speech else 0.4,
            "mode": "real_vad"
        }]

    except Exception as e:
        print("⚠ Audio processing error:", e)
        return [{
            "type": "audio_alert",
            "value": False,
            "confidence": 0.3,
            "mode": "error_fallback"
        }]
