// frontend/src/AlertsPanel.js
import React, { useEffect, useRef, useState } from "react";

function AlertsPanel({ alerts }) {
  const lastAlertRef = useRef(null);
  const alertAudioRef = useRef(null);
  const containerRef = useRef(null);

  const [filteredAlerts, setFilteredAlerts] = useState([]);
  const [riskFilter, setRiskFilter] = useState("");
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [studentFilter, setStudentFilter] = useState("");
  const [eventTypeFilter, setEventTypeFilter] = useState("");

  const [allStudents, setAllStudents] = useState([]);
  const [allEventTypes, setAllEventTypes] = useState([]);

  // -----------------------------
  // DEMO MODE FLAG
  // -----------------------------
  const DEMO_MODE = true;

  // -----------------------------
  // INITIALIZE AUDIO
  // -----------------------------
  useEffect(() => {
    alertAudioRef.current = new Audio("/alert.mp3");
  }, []);

  // -----------------------------
  // DYNAMIC FILTER OPTIONS
  // -----------------------------
  useEffect(() => {
    const students = Array.from(new Set(alerts.map(a => a.student_id ?? "").filter(Boolean)));
    const eventTypes = Array.from(
      new Set(alerts.flatMap(a => a.events?.map(e => e?.type ?? "") || []).filter(Boolean))
    );
    setAllStudents(students);
    setAllEventTypes(eventTypes);
  }, [alerts]);

  // -----------------------------
  // SIMULATE LIVE ALERTS FOR DEMO
  // -----------------------------
  useEffect(() => {
    if (!DEMO_MODE) return;

    const alertTypes = ["multiple_faces", "gaze_deviation", "unauthorized_object", "background_speech"];
    const riskLevels = ["LOW", "MEDIUM", "HIGH"];

    const demoInterval = setInterval(() => {
      const studentId = `student_${Math.floor(Math.random() * 30) + 1}`;
      const level = riskLevels[Math.floor(Math.random() * riskLevels.length)];
      const type = alertTypes[Math.floor(Math.random() * alertTypes.length)];

      const newAlert = {
        student_id: studentId,
        events: [{ type }],
        level,
        score: Math.floor(Math.random() * 100),
        timestamp: new Date().toLocaleTimeString(),
        explanation: `Simulated ${type} detected.`,
        image: `/demo_frames/frame_${Math.floor(Math.random() * 5) + 1}.jpg`,
      };

      setFilteredAlerts(prev => [newAlert, ...prev.slice(0, 49)]);
      lastAlertRef.current = newAlert;

      if (level === "HIGH" && soundEnabled) {
        alertAudioRef.current.play().catch(() => {});
      }

      if (containerRef.current) {
        containerRef.current.scrollTop = 0;
      }
    }, 5000); // new alert every 5 sec

    return () => clearInterval(demoInterval);
  }, [soundEnabled]);

  // -----------------------------
  // HANDLE FILTERED ALERTS
  // -----------------------------
  useEffect(() => {
    if (!alerts || alerts.length === 0) {
      setFilteredAlerts([]);
      return;
    }

    let updatedAlerts = [...alerts];

    if (riskFilter) updatedAlerts = updatedAlerts.filter(a => (a.level ?? "") === riskFilter);
    if (studentFilter) updatedAlerts = updatedAlerts.filter(a => String(a.student_id ?? "") === studentFilter);
    if (eventTypeFilter) updatedAlerts = updatedAlerts.filter(
      a => (a.events ?? []).some(e => (e?.type ?? "") === eventTypeFilter) || (a.type ?? "") === eventTypeFilter
    );

    updatedAlerts = updatedAlerts.slice(0, 50);
    setFilteredAlerts(updatedAlerts);

    const latestAlert = alerts[0];
    if (latestAlert && (latestAlert.level ?? "") === "HIGH" && soundEnabled) {
      alertAudioRef.current.play().catch(() => {});
    }

    if (containerRef.current) containerRef.current.scrollTop = 0;
  }, [alerts, riskFilter, studentFilter, eventTypeFilter, soundEnabled]);

  // -----------------------------
  // ALERT STYLE
  // -----------------------------
  const getAlertClass = (level) => {
    switch (level ?? "") {
      case "HIGH": return "high-alert flash-alert";
      case "MEDIUM": return "medium-alert glow-alert";
      case "LOW": return "low-alert";
      default: return "";
    }
  };

  const clearAlerts = () => setFilteredAlerts([]);

  // -----------------------------
  // UI
  // -----------------------------
  return (
    <div className="alert-panel">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "5px" }}>
        <h3>🚨 Critical Alerts</h3>
        <div style={{ display: "flex", gap: "5px" }}>
          <select value={studentFilter} onChange={e => setStudentFilter(e.target.value)}>
            <option value="">All Students</option>
            {allStudents.map(student => <option key={student} value={student}>{student}</option>)}
          </select>

          <select value={eventTypeFilter} onChange={e => setEventTypeFilter(e.target.value)}>
            <option value="">All Event Types</option>
            {allEventTypes.map(type => <option key={type} value={type}>{type}</option>)}
          </select>

          <select value={riskFilter} onChange={e => setRiskFilter(e.target.value)}>
            <option value="">All Risk Levels</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>

          <button onClick={clearAlerts}>🧹 Clear</button>
          <button onClick={() => setSoundEnabled(!soundEnabled)}>
            {soundEnabled ? "🔊 Sound On" : "🔇 Sound Off"}
          </button>
        </div>
      </div>

      <div ref={containerRef} style={{ maxHeight: "400px", overflowY: "auto" }}>
        {filteredAlerts.length === 0 ? (
          <p style={{ color: "#94a3b8", fontStyle: "italic" }}>No alerts yet</p>
        ) : (
          filteredAlerts.map((alert, idx) => (
            <div key={idx} className={`alert-item ${getAlertClass(alert.level)}`}
              style={{ padding: "8px", marginBottom: "6px", borderRadius: "6px", transition: "all 0.3s ease" }}>
              <p><b>⚠ {alert.level ?? "N/A"}</b> | Score: {alert.score ?? 0}</p>
              <p>Student: {alert.student_id ?? "Unknown"}</p>
              <p>{alert.explanation ?? alert.message ?? "No details available"}</p>
              {alert.timestamp && <p style={{ fontSize: "11px", color: "#94a3b8" }}>🕒 {alert.timestamp}</p>}
              {alert.image && (
                <img
                  src={alert.image}
                  alt="Evidence"
                  style={{
                    width: "100%",
                    maxWidth: "250px",
                    marginTop: "5px",
                    borderRadius: "6px",
                    border: (alert.level ?? "") === "HIGH" ? "2px solid #ef4444" :
                            (alert.level ?? "") === "MEDIUM" ? "2px solid #ff9900" : "2px solid #22c55e",
                    transition: "transform 0.2s ease, box-shadow 0.2s ease"
                  }}
                  onMouseOver={e => {
                    e.currentTarget.style.transform = "scale(1.05)";
                    e.currentTarget.style.boxShadow = "0 0 15px #38bdf8";
                  }}
                  onMouseOut={e => {
                    e.currentTarget.style.transform = "scale(1)";
                    e.currentTarget.style.boxShadow = "none";
                  }}
                />
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default AlertsPanel;