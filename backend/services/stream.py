import cv2
import asyncio
import base64
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from multi_camera_manager import MultiCameraManager

# -----------------------------
# LOGGING
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stream")

# -----------------------------
# FASTAPI APP
# -----------------------------
app = FastAPI(title="SentinelAI Camera Streaming Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# CAMERA MANAGER
# -----------------------------
multi_camera_manager = MultiCameraManager(
    registry_path="backend/config/camera_registry.json",
    resize_width=640
)

# -----------------------------
# START CAMERAS
# -----------------------------
@app.on_event("startup")
async def startup_event():
    logger.info("Starting all camera streams...")
    multi_camera_manager.start_all()
    logger.info("All camera streams started")

# -----------------------------
# STOP CAMERAS
# -----------------------------
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Stopping all camera streams...")
    multi_camera_manager.stop_all()
    logger.info("All camera streams stopped")

# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.get("/")
def home():
    return {"status": "Camera Streaming Service Running"}

@app.get("/health")
def health():
    return {"status": "ok"}

# -----------------------------
# GET CAMERA LIST
# -----------------------------
@app.get("/cameras")
def get_cameras():
    cameras = []

    for cam_id in multi_camera_manager.cameras:
        cameras.append({
            "camera_id": cam_id,
            "student_id": multi_camera_manager.metadata[cam_id]["student_id"]
        })

    return cameras

# -----------------------------
# WEBSOCKET STREAM
# -----------------------------
@app.websocket("/ws/streams")
async def stream_ws(websocket: WebSocket):

    await websocket.accept()
    logger.info("WebSocket connected")

    try:
        while True:

            all_frames = multi_camera_manager.get_all_frames()

            payload = {}

            for cam_id, data in all_frames.items():

                frame = data["frame"]
                student_id = data["student_id"]
                timestamp = data["timestamp"]

                if frame is None:
                    continue

                # Encode frame
                success, buffer = cv2.imencode(".jpg", frame)

                if not success:
                    continue

                jpg_as_text = base64.b64encode(buffer).decode("utf-8")

                payload[cam_id] = {
                    "student_id": student_id,
                    "timestamp": timestamp,
                    "frame": jpg_as_text
                }

            if payload:
                await websocket.send_json(payload)

            await asyncio.sleep(0.1)  # 10 FPS

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

    except Exception as e:
        logger.error(f"Streaming error: {e}")

# -----------------------------
# SINGLE CAMERA STREAM
# -----------------------------
@app.websocket("/ws/stream/{camera_id}")
async def single_camera_stream(websocket: WebSocket, camera_id: str):

    await websocket.accept()
    logger.info(f"WebSocket connected for camera {camera_id}")

    try:
        while True:

            data = multi_camera_manager.get_frame(camera_id)

            if data and data["frame"] is not None:

                frame = data["frame"]
                timestamp = data["timestamp"]
                student_id = data["student_id"]

                success, buffer = cv2.imencode(".jpg", frame)

                if success:

                    jpg_as_text = base64.b64encode(buffer).decode("utf-8")

                    await websocket.send_json({
                        "camera_id": camera_id,
                        "student_id": student_id,
                        "timestamp": timestamp,
                        "frame": jpg_as_text
                    })

            await asyncio.sleep(0.1)

    except WebSocketDisconnect:
        logger.info(f"Camera {camera_id} WebSocket disconnected")

    except Exception as e:
        logger.error(f"Camera {camera_id} stream error: {e}")

# -----------------------------
# SNAPSHOT API
# -----------------------------
@app.get("/snapshot/{camera_id}")
def snapshot(camera_id: str):

    data = multi_camera_manager.get_frame(camera_id)

    if data is None:
        return {"error": "Camera not found"}

    frame = data["frame"]

    if frame is None:
        return {"error": "No frame available"}

    success, buffer = cv2.imencode(".jpg", frame)

    if not success:
        return {"error": "Encoding failed"}

    jpg_as_text = base64.b64encode(buffer).decode("utf-8")

    return {
        "camera_id": camera_id,
        "student_id": data["student_id"],
        "timestamp": data["timestamp"],
        "frame": jpg_as_text
    }

# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "stream:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
