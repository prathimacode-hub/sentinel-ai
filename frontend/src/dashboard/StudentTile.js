// frontend/src/StudentTile.js
import React, { useEffect, useState, useRef } from "react";
import { analyzeFrame } from "../api";

function StudentTile({ id, highlight, overlayImage, lastEvent, camera_id }) {
  const [status, setStatus] = useState("safe");
  const [score, setScore] = useState(0);
  const [isFlashing, setIsFlashing] = useState(false);
  const [cameraError, setCameraError] = useState(false);

  const imgRef = useRef(null);
  const analyzingRef = useRef(false);

  // -----------------------------
  // DEMO MODE SIMULATION
  // -----------------------------
  const DEMO_MODE = true;

  useEffect(() => {
    if (!DEMO_MODE) return;

    const interval = setInterval(() => {
      // Randomly simulate AI score
      const randomScore = Math.floor(Math.random() * 100);
      setScore(randomScore);

      if (randomScore > 60) {
        setStatus("high");
        triggerFlash();
      } else if (randomScore > 30) {
        setStatus("medium");
      } else {
        setStatus("safe");
      }
    }, 4000); // every 4 seconds

    return () => clearInterval(interval);
  }, []);

  // -----------------------------
  // HANDLE LIVE FRAMES
  // -----------------------------
  useEffect(() => {
    if (DEMO_MODE) return; // skip real frame analysis in demo

    const updateFrame = () => {
      if (!imgRef.current || analyzingRef.current) return;

      const canvas = document.createElement("canvas");
      canvas.width = imgRef.current.naturalWidth || 640;
      canvas.height = imgRef.current.naturalHeight || 480;

      const ctx = canvas.getContext("2d");
      ctx.drawImage(imgRef.current, 0, 0, canvas.width, canvas.height);

      analyzingRef.current = true;
      canvas.toBlob(async (blob) => {
        if (!blob) {
          analyzingRef.current = false;
          return;
        }

        try {
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
        } catch (err) {
          console.error("Frame analysis error:", err);
        }
        analyzingRef.current = false;
      }, "image/jpeg");
    };

    const wsListener = (data) => {
      if (data.type === "STREAM_FRAMES" && data.frames[camera_id]) {
        imgRef.current.src = "data:image/jpeg;base64," + data.frames[camera_id];
        updateFrame();
      }
    };

    window.addEventListener(`ws-frame-${camera_id}`, wsListener);
    return () => window.removeEventListener(`ws-frame-${camera_id}`, wsListener);
  }, [camera_id]);

  // -----------------------------
  // FLASH ALERT
  // -----------------------------
  const triggerFlash = () => {
    setIsFlashing(true);
    setTimeout(() => setIsFlashing(false), 2000);
  };

  // -----------------------------
  // TAB SWITCH DETECTION
  // -----------------------------
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        fetch(`http://127.0.0.1:8000/tab-switch/${id}`, { method: "POST" }).catch(() => {});
      }
    };
    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => document.removeEventListener("visibilitychange", handleVisibilityChange);
  }, [id]);

  // -----------------------------
  // RENDER UI
  // -----------------------------
  return (
    <div
      className={`tile ${status} ${highlight ? "highlight" : ""} ${isFlashing ? "flash" : ""}`}
      style={{
        position: "relative",
        transition: "all 0.3s ease-in-out",
        boxShadow: highlight || isFlashing ? "0 0 15px red" : "0 0 5px rgba(0,0,0,0.1)",
      }}
    >
      <h4>🎓 Student {id}</h4>

      {/* Live Camera Feed */}
      <img
        ref={imgRef}
        id={camera_id}
        alt={`Student ${id}`}
        src="/placeholder.png" // fallback placeholder for demo
        onError={() => setCameraError(true)}
        style={{
          width: "200px",
          height: "150px",
          border: highlight ? "3px solid red" : "1px solid #ccc",
          borderRadius: "6px",
        }}
      />

      {cameraError && <p style={{ color: "red" }}>Camera feed unavailable</p>}

      {/* Score & Status */}
      <p>
        <b>Score:</b> {score}
      </p>
      <p>
        <b>Status:</b> {status.toUpperCase()}
      </p>

      {/* Last Event */}
      {lastEvent && (
        <div style={{ marginTop: "5px" }}>
          <p>
            <b>Last Event:</b> {lastEvent.level || lastEvent.events?.map(e => e.type).join(", ")}
          </p>
          <p style={{ fontSize: "12px", color: "#94a3b8" }}>
            {lastEvent.explanation || ""}
          </p>
        </div>
      )}

      {/* Overlay Evidence */}
      {overlayImage && (
        <div className="evidence-box">
          <img
            src={overlayImage}
            alt="evidence"
            onError={(e) => (e.target.style.display = "none")}
            style={{
              marginTop: "5px",
              borderRadius: "8px",
              width: "100%",
              maxHeight: "150px",
              objectFit: "cover",
              border: "2px solid #f87171",
            }}
          />
        </div>
      )}
    </div>
  );
}

export default StudentTile;