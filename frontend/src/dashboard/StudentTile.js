import React, { useRef, useEffect, useState } from "react";
import { analyzeFrame } from "../api";

function StudentTile({ id, highlight }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const [status, setStatus] = useState("safe");
  const [score, setScore] = useState(0);
  const [isFlashing, setIsFlashing] = useState(false);

  useEffect(() => {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        videoRef.current.srcObject = stream;
      });
  }, []);

  useEffect(() => {
    const interval = setInterval(captureFrame, 4000);
    return () => clearInterval(interval);
  });

  const captureFrame = async () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;

    if (!video) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    canvas.toBlob(async (blob) => {
      const result = await analyzeFrame(blob);

      const scoreVal = result?.score?.total_score || 0;
      setScore(scoreVal);

      let currentStatus = "safe";

      if (scoreVal > 60) {
        currentStatus = "high";
        triggerFlash();
      } else if (scoreVal > 30) {
        currentStatus = "medium";
      }

      setStatus(currentStatus);
    });
  };

  const triggerFlash = () => {
    setIsFlashing(true);
    setTimeout(() => setIsFlashing(false), 2000);
  };

  return (
    <div className={`tile ${status} ${highlight ? "highlight" : ""} ${isFlashing ? "flash" : ""}`}>
      <h4>Student {id}</h4>

      <video ref={videoRef} autoPlay muted />

      <canvas ref={canvasRef} style={{ display: "none" }} />

      <p><b>Score:</b> {score}</p>
      <p><b>Status:</b> {status.toUpperCase()}</p>
    </div>
  );
}

export default StudentTile;
