import webrtcvad
import numpy as np
import random

vad = webrtcvad.Vad()
vad.set_mode(2)  # Aggressiveness: 0–3

def detect_audio(audio_bytes=None):
    """
    Detect speech in audio
    NOTE: For hackathon, we simulate or extend later
    """

    # If real audio not passed → simulate
    if audio_bytes is None:
        return {
            "speech_detected": random.choice([True, False])
        }

    # Real VAD processing (if audio provided)
    try:
        is_speech = vad.is_speech(audio_bytes, sample_rate=16000)

        return {
            "speech_detected": is_speech
        }

    except Exception:
        return {
            "speech_detected": False
        }
