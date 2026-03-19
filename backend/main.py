from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import time

from config import settings

# Detection Modules
from detection.face import detect_face
from detection.object import detect_objects
from detection.gaze import detect_gaze
from detection.audio import detect_audio

# Engines
from engine.behavior import analyze_behavior
from engine.scoring import calculate_score
from engine.event_engine import generate_event

# Services
from services.evidence import save_evidence
from services.alert import send_alert

# Utils
from utils.hash_utils import generate_hash

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

# Enable CORS (for frontend integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/")
def home():
    return {
        "message": f"{settings.APP_NAME} is running 🚀",
        "version": settings.VERSION
    }


# -----------------------------
# FRAME ANALYSIS ENDPOINT
# -----------------------------
@app.post("/analyze-frame/")
async def analyze_frame(file: UploadFile = File(...)):
    start_time = time.time()

    try:
        # Read image
        contents = await file.read()
        np_arr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if frame is None:
            return {"error": "Invalid image file"}

        # -----------------------------
        # DETECTION LAYER
        # -----------------------------
        face_data = detect_face(frame)
        object_data = detect_objects(frame)
        gaze_data = detect_gaze(frame)
        audio_data = detect_audio()  # simulated

        # -----------------------------
        # BEHAVIOR ANALYSIS
        # -----------------------------
        behavior = analyze_behavior(
            face_data,
            object_data,
            gaze_data,
            audio_data
        )

        # -----------------------------
        # SCORING
        # -----------------------------
        score = calculate_score(behavior)

        # -----------------------------
        # EVENT GENERATION
        # -----------------------------
        event = generate_event(score, behavior)

        # -----------------------------
        # EVIDENCE CAPTURE
        # -----------------------------
        evidence_path = None
        if event["level"] in ["MEDIUM", "HIGH"]:
            evidence_path = save_evidence(frame, event["level"])

        # -----------------------------
        # HASH LOG (TAMPER-PROOF)
        # -----------------------------
        log_data = {
            "behavior": behavior,
            "score": score,
            "event": event
        }
        log_hash = generate_hash(log_data)

        # -----------------------------
        # ALERT SYSTEM
        # -----------------------------
        if event["level"] == "HIGH":
            send_alert(event)

        processing_time = round(time.time() - start_time, 2)

        return {
            "status": "success",
            "processing_time_sec": processing_time,
            "behavior": behavior,
            "score": score,
            "event": event,
            "evidence": evidence_path,
            "log_hash": log_hash
        }

    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# BULK ANALYSIS (FOR VIDEO FRAMES)
# -----------------------------
@app.post("/analyze-batch/")
async def analyze_batch(files: list[UploadFile]):
    results = []

    for file in files:
        result = await analyze_frame(file)
        results.append(result)

    return {"results": results}


# -----------------------------
# SYSTEM STATUS
# -----------------------------
@app.get("/status")
def system_status():
    return {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "active",
        "features": [
            "Face Detection",
            "Object Detection",
            "Gaze Tracking",
            "Audio Detection",
            "Behavior Analysis",
            "Scoring Engine",
            "Evidence Capture",
            "Tamper-proof Logs"
        ]
    }

# -----------------------------
# WEBSOCKET CONNECTION (REAL-TIME ALERTS)
# -----------------------------
from fastapi import WebSocket, WebSocketDisconnect

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
