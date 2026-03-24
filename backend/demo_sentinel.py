# demo_sentinel.py - Sentinel-AI live demo for gaze + event engine
import cv2
import time
from backend.detection.gaze import gaze_detector
from backend.engine.event_engine import event_engine
from backend.engine.behavior import analyze_behavior
from backend.engine.scoring import calculate_score

STUDENT_ID = "student_demo"

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Cannot access webcam")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # -----------------------------
    # Process frame through event engine
    result = event_engine.process_frame(student_id=STUDENT_ID, frame=frame, simulate=False)

    # -----------------------------
    # Extract gaze
    gaze_output = gaze_detector.process_frame(frame)
    gaze_data = gaze_output[0] if gaze_output else {}

    # -----------------------------
    # Simulate object/audio data for demo
    object_data = {"objects": [], "obstruction": False}
    audio_data = {"speech_detected": False}

    # -----------------------------
    # Analyze behavior
    face_data = {"face_count": len(gaze_output), "identity": {"match": True}}
    behavior_flags = analyze_behavior(face_data, object_data, gaze_data, audio_data)

    # -----------------------------
    # Calculate score
    score_result = calculate_score(behavior_flags)

    # -----------------------------
    # Display overlays
    for idx, face in enumerate(gaze_output):
        hp = face["head_pose"]
        ed = face["eye_direction"]
        cv2.putText(frame, f"Head Pose: Pitch {hp[0]:.1f} Yaw {hp[1]:.1f} Roll {hp[2]:.1f}", (10, 30 + idx * 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, f"Eye Direction: {ed}", (10, 60 + idx * 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Show risk score
    cv2.putText(frame, f"Score: {score_result['total_score']} | Risk: {score_result['risk_level']}",
                (10, frame.shape[0] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 0, 255) if score_result["risk_level"] == "HIGH" else
                (0, 255, 255) if score_result["risk_level"] == "MEDIUM" else
                (0, 255, 0), 2)

    cv2.imshow("Sentinel-AI Demo", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
