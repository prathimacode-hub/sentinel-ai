// frontend/src/Dashboard.js
import React, { useState, useEffect, useRef } from "react";

import Navbar from "./Navbar";
import StudentTile from "./StudentTile";
import AlertsPanel from "./AlertsPanel";
import Timeline from "./Timeline";
import Analytics from "./Analytics";
import AdminPanel from "./AdminPanel";

import { fetchCameraRegistry } from "../api";
import { connectSocket, unsubscribe } from "../socket";
import { initStudentMonitoring } from "../exam"; // <- Modular webcam + WS

function Dashboard({ mode, setMode, eventsProp = [], alertsProp = [], systemStatus = "connecting" }) {
  const DEMO_MODE = true;
  const FALLBACK_IMAGE = "/public/placeholder.png"; // fallback when WS disconnected

  // -----------------------------
  // STATE
  // -----------------------------
  const [cameraRegistry, setCameraRegistry] = useState({ students: [], cctv: [] });
  const [alerts, setAlerts] = useState(alertsProp);
  const [events, setEvents] = useState(eventsProp);
  const [highlightId, setHighlightId] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState(systemStatus);

  const [filterStudentId, setFilterStudentId] = useState("");
  const [filterRiskLevel, setFilterRiskLevel] = useState("");
  const [filterEventType, setFilterEventType] = useState("");

  const alertSound = useRef(null);

  // -----------------------------
  // ALERT SOUND
  // -----------------------------
  useEffect(() => {
    alertSound.current = new Audio("/alert.mp3");
  }, []);

  // -----------------------------
  // FETCH CAMERA REGISTRY
  // -----------------------------
  useEffect(() => {
    async function loadRegistry() {
      try {
        const data = await fetchCameraRegistry();
        setCameraRegistry({
          students: data.students || [],
          cctv: data.hall_cctv || []
        });
      } catch (error) {
        console.error("Camera registry fetch failed:", error);
        // fallback simulation for 30 students
        const simStudents = Array.from({ length: 30 }, (_, i) => ({
          student_id: `student_${i + 1}`,
          camera_id: `sim_cam_${i + 1}`
        }));
        setCameraRegistry({ students: simStudents, cctv: [] });
      }
    }
    loadRegistry();
  }, []);

  // -----------------------------
  // INITIALIZE STUDENT MONITORING (Webcam + WS)
  // -----------------------------
  useEffect(() => {
    if (mode === "live" && cameraRegistry.students.length > 0) {
      cameraRegistry.students.forEach(student => {
        const feedId = `img-${student.student_id}`;
        const overlayId = `overlay-${student.student_id}`;

        // Only create overlay if it doesn’t exist
        if (!document.getElementById(overlayId)) {
          const container = document.getElementById(feedId)?.parentElement;
          if (container) {
            const overlay = document.createElement("div");
            overlay.id = overlayId;
            overlay.className = "overlay";
            overlay.textContent = "Monitoring Active ✅";
            container.appendChild(overlay);
          }
        }

        initStudentMonitoring({
          feedId,
          overlayId,
          wsUrl: "ws://127.0.0.1:8000/ws/student"
        });
      });
    }
  }, [mode, cameraRegistry]);

  // -----------------------------
  // WEBSOCKET FOR ALERTS / EVENTS
  // -----------------------------
  useEffect(() => {
    const listener = (data) => {
      setConnectionStatus("connected");

      if (data.type === "ALERT") {
        const eventData = data.data || data;
        const matchesFilter =
          (!filterStudentId || eventData.student_id === filterStudentId) &&
          (!filterRiskLevel || eventData.risk_level === filterRiskLevel) &&
          (!filterEventType || (eventData.events?.some(e => e.type === filterEventType)));

        if (!matchesFilter) return;

        setAlerts(prev => [eventData, ...prev.slice(0, 50)]);
        setEvents(prev => [eventData, ...prev.slice(0, 200)]);

        if (eventData.risk_level === "HIGH") {
          alertSound.current?.play().catch(() => {});
        }

        if (eventData.student_id) {
          setHighlightId(eventData.student_id);
          setTimeout(() => setHighlightId(null), 4000);
        }
      }
    };

    connectSocket(listener);
    return () => {
      unsubscribe(listener);
      setConnectionStatus("disconnected");

      // Apply fallback images if disconnected
      cameraRegistry.students.forEach(student => {
        const imgEl = document.getElementById(`img-${student.student_id}`);
        if (imgEl) imgEl.src = FALLBACK_IMAGE;
      });
      cameraRegistry.cctv.forEach(cctv => {
        const imgEl = document.getElementById(`img-${cctv.camera_id}`);
        if (imgEl) imgEl.src = FALLBACK_IMAGE;
      });
    };
  }, [filterStudentId, filterRiskLevel, filterEventType, cameraRegistry]);

  // -----------------------------
  // RENDER STUDENT GRID
  // -----------------------------
  const renderStudentGrid = () =>
    cameraRegistry.students.map(student => {
      const lastEvent = events.find(ev => ev.student_id === student.student_id) || null;
      return (
        <div key={student.student_id} className="student-tile-wrapper">
          <StudentTile
            id={student.student_id}
            highlight={highlightId === student.student_id}
            overlayImage={lastEvent?.image || ""}
            lastEvent={lastEvent}
            camera_id={student.camera_id}
          >
            <img
              id={`img-${student.student_id}`}
              alt={student.student_id}
              src={FALLBACK_IMAGE}
              style={{
                width: "320px",
                height: "240px",
                borderRadius: "8px",
                border: highlightId === student.student_id ? "3px solid red" : "1px solid #444"
              }}
            />
          </StudentTile>
        </div>
      );
    });

  // -----------------------------
  // RENDER CCTV GRID
  // -----------------------------
  const renderCCTVGrid = () =>
    cameraRegistry.cctv.map(cctv => (
      <div key={cctv.camera_id} className="cctv-tile-wrapper">
        <h4>{cctv.label}</h4>
        <img
          id={`img-${cctv.camera_id}`}
          alt={cctv.label}
          src={FALLBACK_IMAGE}
          style={{
            width: "400px",
            height: "250px",
            border: "1px solid #444",
            borderRadius: "8px"
          }}
        />
      </div>
    ));

  // -----------------------------
  // UI
  // -----------------------------
  return (
    <div className="dashboard">
      <Navbar setMode={setMode} systemStatus={connectionStatus} />

      <div className="connection-status" style={{ color: connectionStatus === "connected" ? "#22c55e" : "#ef4444" }}>
        System Status: {connectionStatus === "connected" ? "🟢 Connected" : "🔴 Disconnected"}
      </div>

      {mode === "live" && (
        <>
          <h2>🎥 Live Monitoring</h2>

          <div className="filters">
            <input
              type="text"
              placeholder="Filter by Student ID"
              value={filterStudentId}
              onChange={e => setFilterStudentId(e.target.value)}
            />
            <select value={filterRiskLevel} onChange={e => setFilterRiskLevel(e.target.value)}>
              <option value="">All Risk Levels</option>
              <option value="LOW">LOW</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="HIGH">HIGH</option>
            </select>
            <input
              type="text"
              placeholder="Filter by Event Type"
              value={filterEventType}
              onChange={e => setFilterEventType(e.target.value)}
            />
          </div>

          <div className="student-grid">{renderStudentGrid()}</div>
          <div className="cctv-grid">{renderCCTVGrid()}</div>

          <AlertsPanel alerts={alerts} />
          <Timeline events={events} />
        </>
      )}

      {mode === "analytics" && <Analytics events={events} />}
      {mode === "admin" && <AdminPanel />}
    </div>
  );
}

export default Dashboard;