import React, { useState, useEffect } from "react";
import StudentTile from "./StudentTile";
import AlertsPanel from "./AlertsPanel";
import Timeline from "./Timeline";
import Navbar from "./Navbar";
import { checkBackendStatus } from "../api";

function Dashboard() {
  const [alerts, setAlerts] = useState([]);
  const [events, setEvents] = useState([]);
  const [backendStatus, setBackendStatus] = useState("offline");

  // Check backend health
  useEffect(() => {
    const checkStatus = async () => {
      const res = await checkBackendStatus();
      setBackendStatus(res.message ? "online" : "offline");
    };

    checkStatus();
    const interval = setInterval(checkStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleNewEvent = (event) => {
    setEvents((prev) => [event, ...prev]);

    if (event.level === "HIGH") {
      setAlerts((prev) => [event, ...prev]);
    }
  };

  return (
    <div className="dashboard">
      <Navbar status={backendStatus} />

      <h2>🎥 Live Monitoring</h2>

      <div className="grid">
        {[1, 2, 3, 4, 5, 6].map((id) => (
          <StudentTile key={id} id={id} onEvent={handleNewEvent} />
        ))}
      </div>

      <AlertsPanel alerts={alerts} />
      <Timeline events={events} />
    </div>
  );
}

export default Dashboard;
