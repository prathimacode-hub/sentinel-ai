// frontend/src/Navbar.js
import React, { useState } from "react";

function Navbar({ setMode, systemStatus, mode }) {
  const [activeMode, setActiveMode] = useState(mode || "live");

  // -----------------------------
  // HANDLE MODE CHANGE
  // -----------------------------
  const handleModeChange = (newMode) => {
    setActiveMode(newMode);
    setMode(newMode);
  };

  // -----------------------------
  // STATUS LABEL
  // -----------------------------
  const getStatusLabel = () => {
    switch (systemStatus) {
      case "connected":
      case "online":
        return "🟢 System Online";
      case "disconnected":
      case "offline":
        return "🔴 System Offline";
      default:
        return "🟡 Connecting...";
    }
  };

  // -----------------------------
  // BUTTON STYLES
  // -----------------------------
  const getButtonStyle = (buttonMode) => ({
    padding: "6px 12px",
    margin: "0 4px",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
    color: "#fff",
    backgroundColor: activeMode === buttonMode ? "#22c55e" : "#38bdf8",
    transition: "background 0.2s",
  });

  // -----------------------------
  // UI
  // -----------------------------
  return (
    <div
      className="navbar"
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "10px 20px",
        backgroundColor: "#1e293b",
        color: "#f1f5f9",
      }}
    >
      {/* Logo / Title */}
      <h1 style={{ fontSize: "18px", margin: 0 }}>SentinelAI Dashboard 🎯</h1>

      {/* Controls */}
      <div style={{ display: "flex", alignItems: "center" }}>
        {/* Mode Buttons */}
        <button style={getButtonStyle("live")} onClick={() => handleModeChange("live")}>
          🎥 Live
        </button>
        <button style={getButtonStyle("analytics")} onClick={() => handleModeChange("analytics")}>
          📊 Analytics
        </button>
        <button style={getButtonStyle("admin")} onClick={() => handleModeChange("admin")}>
          ⚙ Admin
        </button>

        {/* Optional connection status indicator */}
        <div
          className={`status-indicator ${
            systemStatus === "online" || systemStatus === "connected"
              ? "online"
              : systemStatus === "offline" || systemStatus === "disconnected"
              ? "offline"
              : ""
          }`}
          style={{
            marginLeft: "12px",
            fontWeight: "500",
            fontSize: "14px",
          }}
        >
          {getStatusLabel()}
        </div>
      </div>
    </div>
  );
}

export default Navbar;