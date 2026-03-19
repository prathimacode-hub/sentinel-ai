from collections import deque
import time


class FrameBuffer:
    """
    Stores last N frames for video clip generation
    """

    def __init__(self, max_length=50):
        self.buffer = deque(maxlen=max_length)

    def add_frame(self, frame):
        self.buffer.append(frame)

    def get_frames(self):
        return list(self.buffer)

    def clear(self):
        self.buffer.clear()


# -----------------------------
# EVENT CLIP CAPTURE
# -----------------------------
class ClipRecorder:
    def __init__(self, pre_event_frames=20, post_event_frames=20):
        self.pre_buffer = deque(maxlen=pre_event_frames)
        self.post_frames = []
        self.recording = False
        self.post_limit = post_event_frames

    def add_frame(self, frame):
        if not self.recording:
            self.pre_buffer.append(frame)
        else:
            self.post_frames.append(frame)

    def trigger_event(self):
        """
        Start recording post-event frames
        """
        self.recording = True

    def is_done(self):
        return len(self.post_frames) >= self.post_limit

    def get_clip(self):
        """
        Combine pre + post frames
        """
        return list(self.pre_buffer) + self.post_frames

    def reset(self):
        self.pre_buffer.clear()
        self.post_frames = []
        self.recording = False


# -----------------------------
# FPS CALCULATOR (OPTIONAL)
# -----------------------------
class FPSCounter:
    def __init__(self):
        self.start_time = time.time()
        self.frames = 0

    def update(self):
        self.frames += 1

    def get_fps(self):
        elapsed = time.time() - self.start_time
        return self.frames / elapsed if elapsed > 0 else 0
