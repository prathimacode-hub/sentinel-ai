// frontend/src/AdminPanel.js
import React, { useState, useEffect } from "react";
import { connectSocket, unsubscribe } from "../socket";

function AdminPanel({ demoMode = true }) {
  const [threshold, setThreshold] = useState(60);
  const [monitoring, setMonitoring] = useState(false);
  const [systemStatus, setSystemStatus] = useState("offline");
  const [logs, setLogs] = useState([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  // Live stats
  const [studentsConnected, setStudentsConnected] = useState([]);
  const [lastAlerts, setLastAlerts] = useState([]);

  // -----------------------------
  // CHECK SYSTEM HEALTH
  // -----------------------------
  useEffect(() => {
    checkSystemHealth();
    const interval = setInterval(() => checkSystemHealth(), 5000);
    return () => clearInterval(interval);
  }, []);

  const checkSystemHealth = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/health");
      setSystemStatus(res.ok ? "online" : "offline");
    } catch {
      setSystemStatus("offline");
    }
  };

  // -----------------------------
  // MONITORING CONTROLS
  // -----------------------------
  const startMonitoring = async () => {
    setLoading(true);
    try {
      await fetch("http://127.0.0.1:8000/start-monitoring", { method: "POST" });
      setMonitoring(true);
      setMessage("🟢 Monitoring started");
      addLog("Monitoring Started");
    } catch {
      setMessage("🔴 Failed to start monitoring");
    }
    setLoading(false);
  };

  const stopMonitoring = async () => {
    setLoading(true);
    try {
      await fetch("http://127.0.0.1:8000/stop-monitoring", { method: "POST" });
      setMonitoring(false);
      setMessage("🔴 Monitoring stopped");
      addLog("Monitoring Stopped");
    } catch {
      setMessage("Failed to stop monitoring");
    }
    setLoading(false);
  };

  const updateThreshold = async () => {
    try {
      await fetch("http://127.0.0.1:8000/set-threshold", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ threshold }),
      });
      setMessage("⚙ Threshold updated");
      addLog(`Threshold changed to ${threshold}`);
    } catch {
      setMessage("Failed to update threshold");
    }
  };

  const resetEvents = async () => {
    try {
      await fetch("http://127.0.0.1:8000/reset-events", { method: "POST" });
      setMessage("🧹 Events cleared");
      addLog("Events Reset");
      setLastAlerts([]);
    } catch {
      setMessage("Failed to reset events");
    }
  };

  // -----------------------------
  // LOG UTILITIES
  // -----------------------------
  const addLog = (text) => {
    const time = new Date().toLocaleTimeString();
    setLogs((prev) => [`${time} - ${text}`, ...prev]);
  };

  const exportLogs = () => {
    const blob = new Blob([logs.join("\n")], { type: "text/plain" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "sentinel_logs.txt";
    link.click();
    addLog("Logs Exported");
  };

  // -----------------------------
  // SOCKET LISTENER FOR LIVE STATUS
  // -----------------------------
  useEffect(() => {
    if (!demoMode) return;

    const listener = (data) => {
      if (data.type === "STUDENT_STATUS") {
        setStudentsConnected(data.students || []);
      }

      if (data.type === "ALERT") {
        setLastAlerts((prev) => [data.data, ...prev].slice(0, 5));
      }
    };

    connectSocket(listener);
    return () => unsubscribe(listener);
  }, []);

  // -----------------------------
  // MANUAL ALERT TRIGGER (DEMO)
  // -----------------------------
  const triggerDemoAlert = () => {
    const demoAlert = {
      student_id: `student_${Math.ceil(Math.random() * 30)}`,
      events: [{ type: "manual_trigger" }],
      risk_level: ["LOW", "MEDIUM", "HIGH"][Math.floor(Math.random() * 3)],
      timestamp: new Date().toISOString(),
      image: ""
    };

    setLastAlerts((prev) => [demoAlert, ...prev].slice(0, 5));
    addLog(`Manual alert triggered for ${demoAlert.student_id}`);
  };

  // -----------------------------
  // UI
  // -----------------------------
  return (
    <div className="analytics">
      <h2>⚙ SentinelAI Admin Control Panel</h2>

      {/* SYSTEM STATUS */}
      <div className="tile">
        <h3>System Status</h3>
        <p>{systemStatus === "online" ? "🟢 Backend Running" : "🔴 Backend Offline"}</p>
        <p>Monitoring: {monitoring ? "🟢 Active" : "🔴 Stopped"}</p>
        <p>Total Students Connected: {studentsConnected.length}</p>
      </div>

      {/* ALERT THRESHOLD */}
      <div className="tile">
        <h3>Alert Threshold</h3>
        <input
          type="range"
          min="10"
          max="100"
          value={threshold}
          onChange={(e) => setThreshold(e.target.value)}
          style={{ width: "100%" }}
        />
        <p>Current Threshold: {threshold}</p>
        <button onClick={updateThreshold}>Update Threshold</button>
      </div>

      {/* SYSTEM CONTROLS */}
      <div className="tile">
        <h3>System Controls</h3>
        <button onClick={startMonitoring} disabled={loading}>🟢 Start Monitoring</button>
        <button onClick={stopMonitoring} disabled={loading}>🔴 Stop Monitoring</button>
        <button onClick={resetEvents}>🧹 Reset Events</button>
        <button onClick={exportLogs}>📁 Export Logs</button>
        <button onClick={triggerDemoAlert}>⚠ Trigger Demo Alert</button>
      </div>

      {/* LAST 5 ALERTS */}
      <div className="tile">
        <h3>Last 5 Alerts</h3>
        {lastAlerts.length === 0 ? (
          <p>No alerts yet</p>
        ) : (
          <div style={{ maxHeight: "200px", overflowY: "auto", background: "#111827", padding: "10px", borderRadius: "8px" }}>
            {lastAlerts.map((alert, idx) => (
              <p key={idx} style={{ fontSize: "12px", margin: "4px 0", color: "#f59e0b" }}>
                {new Date(alert.timestamp).toLocaleTimeString()} - {alert.student_id} ({alert.risk_level})
              </p>
            ))}
          </div>
        )}
      </div>

      {/* LOGS PANEL */}
      <div className="tile">
        <h3>📜 System Logs</h3>
        {logs.length === 0 ? (
          <p>No logs yet</p>
        ) : (
          <div style={{ maxHeight: "200px", overflowY: "auto", background: "#111827", padding: "10px", borderRadius: "8px" }}>
            {logs.map((log, index) => (
              <p key={index} style={{ fontSize: "12px", margin: "4px 0", color: "#94a3b8" }}>{log}</p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default AdminPanel;