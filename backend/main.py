from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
import cv2
import numpy as np
import asyncio

# Detection
from detection.face import detect_faces
from detection.object import detect_objects
from detection.gaze import detect_gaze
from detection.audio import detect_audio
from detection.identity import identity_verifier
from detection.obstruction import detect_obstruction

# Engine
from engine.behavior import analyze_behavior
from engine.scoring import calculate_score
from engine.event_engine import generate_event

# Services
from services.alert import manager, send_alert, broadcast_alert
from services.storage import storage

# Utils
from utils.video_utils import FrameBuffer

# DB
from database.db import engine, get_db
from database.models import Base, Event

# Init DB
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SentinelAI Backend")

# -----------------------------
# GLOBAL BUFFER (for demo)
# -----------------------------
frame_buffer = FrameBuffer(max_length=30)


# -----------------------------
# WEBSOCKET
# -----------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/")
def home():
    return {"message": "SentinelAI Running 🚀"}


# -----------------------------
# REGISTER STUDENT FACE
# -----------------------------
@app.post("/register/{student_id}")
async def register_student(student_id: str, file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    result = identity_verifier.register_student(student_id, frame)
    return result


# -----------------------------
# TAB SWITCH EVENT
# -----------------------------
@app.post("/tab-switch/{student_id}")
async def tab_switch(student_id: str):
    event = {
        "student_id": student_id,
        "level": "MEDIUM",
        "score": 40,
        "explanation": "Tab switch detected",
        "reasons": ["tab_switch"]
    }

    await broadcast_alert(event)
    return {"status": "tab switch recorded"}


# -----------------------------
# MAIN ANALYSIS API
# -----------------------------
@app.post("/analyze-frame/{student_id}")
async def analyze_frame(student_id: str, file: UploadFile = File(...)):
    contents = await file.read()

    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Store frame in buffer
    frame_buffer.add_frame(frame)

    # -----------------------------
    # DETECTION
    # -----------------------------
    face_data = detect_faces(frame)
    object_data = detect_objects(frame)
    gaze_data = detect_gaze(frame)
    audio_data = {"speech": False}  # placeholder

    identity_data = identity_verifier.verify(student_id, frame)
    obstruction_data = detect_obstruction(frame)

    # Combine
    detection_data = {
        "face": face_data,
        "object": object_data,
        "gaze": gaze_data,
        "audio": audio_data,
        "identity": identity_data,
        "obstruction": obstruction_data
    }

    # -----------------------------
    # BEHAVIOR
    # -----------------------------
    behavior = analyze_behavior(detection_data)

    # -----------------------------
    # SCORING
    # -----------------------------
    score = calculate_score(behavior)

    # -----------------------------
    # EVENT GENERATION
    # -----------------------------
    event = generate_event(score, behavior)
    event["student_id"] = student_id

    # -----------------------------
    # SAVE EVIDENCE
    # -----------------------------
    image_path = storage.save_image(frame, prefix=student_id)
    log_path, hash_val = storage.save_event(event)

    # -----------------------------
    # DATABASE ENTRY
    # -----------------------------
    db = next(get_db())

    db_event = Event(
        student_id=student_id,
        level=event["level"],
        score=event["score"],
        explanation=event["explanation"],
        reasons=event["reasons"]
    )

    db.add(db_event)
    db.commit()

    # -----------------------------
    # ALERT
    # -----------------------------
    if event["level"] == "HIGH":
        send_alert(event)
        await broadcast_alert(event)

    return {
        "event": event,
        "evidence": {
            "image": image_path,
            "log": log_path,
            "hash": hash_val
        }
    }

clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)

    print("Client connected. Total:", len(clients))

    try:
        while True:
            await websocket.receive_text()  # keep connection alive
    except WebSocketDisconnect:
        clients.remove(websocket)
        print("Client disconnected. Total:", len(clients))


@app.post("/tab-switch")
async def tab_switch():
    event = {
        "level": "MEDIUM",
        "score": 40,
        "explanation": "Tab switch detected"
    }

    await broadcast_alert(event)
    return {"status": "ok"}
