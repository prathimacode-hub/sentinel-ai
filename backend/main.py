from fastapi import FastAPI, UploadFile
import cv2
import numpy as np

from detection.face import detect_face
from detection.object import detect_objects
from detection.gaze import detect_gaze
from detection.audio import detect_audio

from engine.behavior import analyze_behavior
from engine.scoring import calculate_score
from engine.event_engine import generate_event

app = FastAPI()

@app.get("/")
def home():
    return {"message": "SentinelAI Running 🚀"}


@app.post("/analyze_frame/")
async def analyze_frame(file: UploadFile):
    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    face_data = detect_face(frame)
    object_data = detect_objects(frame)
    gaze_data = detect_gaze(frame)

    behavior = analyze_behavior(face_data, object_data, gaze_data)
    score = calculate_score(behavior)

    event = generate_event(score, behavior)

    return {
        "behavior": behavior,
        "score": score,
        "event": event
    }
