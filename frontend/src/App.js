// src/App.js
import React, { useState, useEffect } from "react";
import "./styles.css";

import Navbar from "./dashboard/Navbar";
import Dashboard from "./dashboard/Dashboard";
import Analytics from "./dashboard/Analytics";
import AdminPanel from "./dashboard/AdminPanel";

import { fetchEvents } from "./api";
import { connectSocket, unsubscribe } from "./socket";

function App() {
  // -----------------------------
  // GLOBAL STATES
  // -----------------------------
  const [mode, setMode] = useState("live"); // live, analytics, admin
  const [events, setEvents] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [systemStatus, setSystemStatus] = useState("connecting");

  // -----------------------------
  // WEBSOCKET HANDLER
  // -----------------------------
  useEffect(() => {
    const listener = (data) => {
      // handle live frame updates and alerts
      if (data.type === "ALERT") {
        setAlerts(prev => [data.data || data, ...prev.slice(0, 50)]);
        setEvents(prev => [data.data || data, ...prev.slice(0, 200)]);
      }
    };

    connectSocket(listener, "dashboard");

    return () => {
      unsubscribe(listener); // cleanup on unmount
    };
  }, []);

  // -----------------------------
  // INITIAL DATA LOAD
  // -----------------------------
  useEffect(() => {
    loadInitialEvents();
  }, []);

  const loadInitialEvents = async () => {
    try {
      const data = await fetchEvents();
      if (Array.isArray(data)) {
        setEvents(data.slice(0, 100)); // latest 100 events
        setAlerts(data.filter((e) => e.risk_level === "HIGH").slice(0, 10));
      }
    } catch (err) {
      console.warn("Failed to load initial events:", err);
    }
  };

  // -----------------------------
  // RENDER SELECTED MODE
  // -----------------------------
  const renderMode = () => {
    switch (mode) {
      case "live":
        return (
          <Dashboard
            mode={mode}
            setMode={setMode}
            eventsProp={events}
            alertsProp={alerts}
            systemStatus={systemStatus}
          />
        );

      case "analytics":
        return <Analytics events={events} />;

      case "admin":
        return <AdminPanel />;

      default:
        return (
          <Dashboard
            mode={mode}
            setMode={setMode}
            eventsProp={events}
            alertsProp={alerts}
            systemStatus={systemStatus}
          />
        );
    }
  };

  // -----------------------------
  // MAIN UI
  // -----------------------------
  return (
    <div className="app">
      <Navbar setMode={setMode} systemStatus={systemStatus} />
      <div className="main-container">{renderMode()}</div>
    </div>
  );
}

export default App;