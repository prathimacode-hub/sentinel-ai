import cv2
import threading
import time

class VideoStream:
    def __init__(self, source=0, name="Camera"):
        """
        source:
            0 = webcam
            rtsp://... = CCTV stream
        """
        self.source = source
        self.name = name
        self.cap = cv2.VideoCapture(source)
        self.frame = None
        self.running = False

    def start(self):
        if self.running:
            return self

        self.running = True
        thread = threading.Thread(target=self.update, daemon=True)
        thread.start()
        return self

    def update(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            self.frame = frame

    def read(self):
        return self.frame

    def stop(self):
        self.running = False
        self.cap.release()


# -----------------------------
# MULTI-STREAM HANDLER
# -----------------------------
class MultiCameraManager:
    def __init__(self):
        self.streams = {}

    def add_camera(self, cam_id, source):
        stream = VideoStream(source, name=f"Camera-{cam_id}").start()
        self.streams[cam_id] = stream

    def get_frame(self, cam_id):
        stream = self.streams.get(cam_id)
        if stream:
            return stream.read()
        return None

    def stop_all(self):
        for stream in self.streams.values():
            stream.stop()
