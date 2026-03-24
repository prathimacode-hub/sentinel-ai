import cv2
import threading
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RTSPStream:
    """
    Handles a single RTSP or USB camera stream in a separate thread.
    Provides latest frame in a thread-safe manner with timestamping.
    """

    def __init__(self, camera_id: str, rtsp_url: str, reconnect_interval: float = 5.0, resize_width: int = None):
        self.camera_id = camera_id
        self.rtsp_url = rtsp_url
        self.reconnect_interval = reconnect_interval
        self.resize_width = resize_width  # optional frame resizing

        self.capture = None
        self.frame = None
        self.timestamp = None  # new: time of latest frame
        self.running = False
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._update_stream, daemon=True)

    def start(self):
        """Start the stream thread"""
        if not self.running:
            self.running = True
            logger.info(f"[{self.camera_id}] Starting stream thread")
            self.thread.start()

    def stop(self):
        """Stop the stream thread and release resources"""
        self.running = False
        if self.capture is not None:
            self.capture.release()
        logger.info(f"[{self.camera_id}] Stream stopped")

    def _init_capture(self):
        """Initialize the VideoCapture object"""
        if self.capture is not None:
            self.capture.release()
        self.capture = cv2.VideoCapture(self.rtsp_url)
        if not self.capture.isOpened():
            logger.warning(f"[{self.camera_id}] Cannot open stream, will retry in {self.reconnect_interval}s")
            return False
        logger.info(f"[{self.camera_id}] Stream opened successfully")
        return True

    def _update_stream(self):
        """Thread target to continuously read frames"""
        while self.running:
            if self.capture is None or not self.capture.isOpened():
                success = self._init_capture()
                if not success:
                    time.sleep(self.reconnect_interval)
                    continue

            ret, frame = self.capture.read()
            if not ret or frame is None:
                logger.warning(f"[{self.camera_id}] Frame read failed, reconnecting...")
                self.capture.release()
                self.capture = None
                time.sleep(self.reconnect_interval)
                continue

            # Resize frame if configured
            if self.resize_width and frame.shape[1] > self.resize_width:
                height = int(frame.shape[0] * (self.resize_width / frame.shape[1]))
                frame = cv2.resize(frame, (self.resize_width, height))

            # Save latest frame with timestamp in thread-safe way
            with self.lock:
                self.frame = frame
                self.timestamp = time.time()

    def get_frame(self):
        """
        Returns the latest frame in BGR format (OpenCV style) and timestamp.
        Returns (frame, timestamp) or (None, None) if no frame yet.
        """
        with self.lock:
            if self.frame is not None:
                return self.frame.copy(), self.timestamp
            else:
                return None, None

    def is_alive(self):
        """Check if stream is running and capture is opened"""
        return self.running and self.capture is not None and self.capture.isOpened()


# --- Demo usage ---
if __name__ == "__main__":
    import time

    # Example RTSP/USB URL (replace with real camera)
    camera = RTSPStream(camera_id="demo_cam", rtsp_url="rtsp://192.168.1.101/stream", resize_width=640)
    camera.start()

    try:
        while True:
            frame, ts = camera.get_frame()
            if frame is not None:
                cv2.putText(frame, f"{camera.camera_id} {time.strftime('%H:%M:%S', time.localtime(ts))}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.imshow("Live Feed", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            time.sleep(0.02)
    except KeyboardInterrupt:
        pass
    finally:
        camera.stop()
        cv2.destroyAllWindows()
