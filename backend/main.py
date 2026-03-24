# backend/main.py
# SentinelAI Backend - Live Multi-Student AI Proctoring Demo
# ------------------------------------------------------------
import os
import time
import json
import cv2
import asyncio
import base64
import logging
import numpy as np
from typing import Dict, Any
from threading import Lock

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from backend.services.multi_camera_manager import MultiCameraManager
from backend.services.recording_manager import RecordingManager
from backend.engine.event_engine import event_engine
from backend.utils.hash_utils import generate_hash, generate_chain_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SentinelAI")

# -----------------------------
# DIR SETUP
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EVIDENCE_DIR = os.path.join(BASE_DIR, "evidence")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
CACHE_DIR = os.path.join(BASE_DIR, "cache")
os.makedirs(EVIDENCE_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

EVIDENCE_LOG = os.path.join(LOGS_DIR, "evidence_log.json")
ANALYTICS_FILE = os.path.join(LOGS_DIR, "analytics.json")
CAMERA_REGISTRY = os.path.join(CONFIG_DIR, "camera_registry.json")

# -----------------------------
# GLOBALS
# -----------------------------
SIMULATION_ENABLED = True
SIMULATION_STUDENT_COUNT = 30
monitoring_active = False
sessions_store: Dict[str, list] = {}
student_ws_clients: Dict[str, set] = {}  # student_id -> set of WebSocket
alerts_ws_clients: set = set()
analytics_data = {"total_events": 0, "high_risk": 0, "medium_risk": 0, "low_risk": 0}
analytics_lock = Lock()
evidence_lock = Lock()

# -----------------------------
# RECORDING MANAGER
# -----------------------------
recording_manager = RecordingManager(buffer_sec=5, fps=10)

# -----------------------------
# FASTAPI INIT
# -----------------------------
app = FastAPI(title="SentinelAI Backend Demo 🚀", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.mount("/evidence", StaticFiles(directory=EVIDENCE_DIR), name="evidence")

# -----------------------------
# CAMERA MANAGER INIT
# -----------------------------
multi_camera_manager = MultiCameraManager(
    registry_path=CAMERA_REGISTRY,
    resize_width=640
)

# -----------------------------
# EVIDENCE + ANALYTICS HELPERS
# -----------------------------
def save_evidence(student_id, frame_bytes, result):
    timestamp = int(time.time())
    filename = f"{student_id}_{timestamp}.jpg"
    filepath = os.path.join(EVIDENCE_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(frame_bytes)

    evidence_data = {
        "student_id": student_id,
        "timestamp": timestamp,
        "file": filename,
        "events": result.get("events", []),
        "score": result.get("score", 0),
        "risk_level": result.get("risk_level", "LOW"),
        "identity_verified": result.get("confidence", 1.0)
    }

    image_hash = generate_hash(filepath)
    with evidence_lock:
        previous_hash = ""
        if os.path.exists(EVIDENCE_LOG):
            with open(EVIDENCE_LOG) as f:
                logs = json.load(f)
            previous_hash = logs[-1]["chain_hash"] if logs else ""
        else:
            logs = []

        chain_hash = generate_chain_hash(evidence_data, previous_hash)
        evidence_data["sha256"] = image_hash
        evidence_data["chain_hash"] = chain_hash

        logs.append(evidence_data)
        with open(EVIDENCE_LOG, "w") as f:
            json.dump(logs, f, indent=4)

def update_analytics(result):
    with analytics_lock:
        analytics_data["total_events"] += 1
        level = result.get("risk_level", "LOW")
        if level == "HIGH":
            analytics_data["high_risk"] += 1
        elif level == "MEDIUM":
            analytics_data["medium_risk"] += 1
        else:
            analytics_data["low_risk"] += 1
        with open(ANALYTICS_FILE, "w") as f:
            json.dump(analytics_data, f)

# -----------------------------
# WEBSOCKET BROADCAST
# -----------------------------
async def broadcast_student_frame(student_id, frame_bytes):
    clients = student_ws_clients.get(student_id, set()).copy()
    dead_clients = set()
    for ws in clients:
        try:
            await ws.send_bytes(frame_bytes)
        except:
            dead_clients.add(ws)
    for ws in dead_clients:
        student_ws_clients[student_id].discard(ws)

async def broadcast_alert(alert_data):
    dead_clients = set()
    for ws in alerts_ws_clients.copy():
        try:
            await ws.send_json(alert_data)
        except:
            dead_clients.add(ws)
    for ws in dead_clients:
        alerts_ws_clients.discard(ws)

# -----------------------------
# REST ENDPOINTS
# -----------------------------
@app.get("/")
def home():
    return {"message": "SentinelAI Running 🚀"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/start_exam")
async def start_exam():
    global monitoring_active
    monitoring_active = True
    logger.info("Exam started")
    return {"status": "started"}

@app.post("/stop_exam")
async def stop_exam():
    global monitoring_active
    monitoring_active = False
    logger.info("Exam stopped")
    return {"status": "stopped"}

@app.get("/alerts")
def get_alerts():
    return event_engine.get_all_alerts()

# -----------------------------
# WEBSOCKET ENDPOINTS
# -----------------------------
@app.websocket("/ws/student/{student_id}")
async def ws_student(websocket: WebSocket, student_id: str):
    await websocket.accept()
    student_ws_clients.setdefault(student_id, set()).add(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        student_ws_clients[student_id].discard(websocket)

@app.websocket("/ws/alerts")
async def ws_alerts(websocket: WebSocket):
    await websocket.accept()
    alerts_ws_clients.add(websocket)
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        alerts_ws_clients.discard(websocket)

# -----------------------------
# LIVE CAMERA PROCESSING LOOP
# -----------------------------
async def live_camera_loop():
    multi_camera_manager.start_all()
    student_ids = [f"student_{i+1}" for i in range(SIMULATION_STUDENT_COUNT)]

    if SIMULATION_ENABLED:
        event_engine.start_demo_mode(student_ids)

    while True:
        if not monitoring_active:
            await asyncio.sleep(0.5)
            continue

        frames = multi_camera_manager.get_all_frames()

        for cam_id, data in frames.items():
            frame = data.get("frame")
            student_id = data.get("student_id") or f"student_{cam_id}"
            if frame is None:
                continue

            # Add frame to recording buffer
            recording_manager.add_frame(student_id, frame)

            try:
                result = event_engine.process_frame(student_id, frame, simulate=SIMULATION_ENABLED)
            except:
                result = event_engine.process_frame(student_id, frame, simulate=True)

            # Overlay faces
            for f in result.get("faces", []):
                bbox = f.get("bbox", [50,50,150,150])
                x1,y1,x2,y2 = bbox
                cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)

            _, buffer = cv2.imencode(".jpg", frame)
            frame_bytes = buffer.tobytes()
            frame_b64 = base64.b64encode(buffer).decode()
            event_engine.update_frame(student_id, frame_b64)

            # Broadcast student frame
            await broadcast_student_frame(student_id, frame_bytes)

            # --- HIGH/MEDIUM ALERT HANDLING ---
            if result["risk_level"] in ["HIGH","MEDIUM"]:
                event_type = result.get("explanation", "AI_Alert").replace(" ", "_")
                event_info = recording_manager.save_event(student_id, frame, event_type)

                save_evidence(student_id, frame_bytes, result)
                update_analytics(result)

                await broadcast_alert({
                    "student_id": student_id,
                    "type": "ALERT",
                    "level": result["risk_level"],
                    "event": result.get("explanation","AI Alert"),
                    "timestamp": int(time.time()),
                    "frame": frame_b64,
                    "snapshot_file": event_info.get("snapshot_file"),
                    "clip_file": event_info.get("clip_file"),
                    "snapshot_hash": event_info.get("snapshot_hash"),
                    "clip_hash": event_info.get("clip_hash")
                })

        await asyncio.sleep(0.5)

# -----------------------------
# STARTUP EVENT
# -----------------------------
@app.on_event("startup")
async def startup():
    logger.info("SentinelAI Backend Starting 🚀")
    if os.path.exists(ANALYTICS_FILE):
        with open(ANALYTICS_FILE) as f:
            analytics_data.update(json.load(f))
    asyncio.create_task(live_camera_loop())
