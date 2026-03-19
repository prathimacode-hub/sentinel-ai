import React, { useState, useEffect } from "react";
import StudentTile from "./StudentTile";
import AlertsPanel from "./AlertsPanel";
import Timeline from "./Timeline";
import Navbar from "./Navbar";
import Analytics from "./Analytics";
import AdminPanel from "./AdminPanel";

import { connectSocket } from "../socket";

function Dashboard() {
  const [alerts, setAlerts] = useState([]);
  const [events, setEvents] = useState([]);
  const [mode, setMode] = useState("live");

  // 🔥 Real-time WebSocket
  useEffect(() => {
    connectSocket((data) => {
      if (data.type === "ALERT") {
        setAlerts((prev) => [data.data, ...prev]);
        setEvents((prev) => [data.data, ...prev]);
      }
    });
  }, []);

  return (
    <div className="dashboard">
      <Navbar setMode={setMode} />

      {mode === "live" && (
        <>
          <h2>🎥 Live Monitoring</h2>
          <div className="grid">
            {[1,2,3,4,5,6].map(id => (
              <StudentTile key={id} id={id} />
            ))}
          </div>

          <AlertsPanel alerts={alerts} />
          <Timeline events={events} />
        </>
      )}

      {mode === "analytics" && <Analytics events={events} />}
      {mode === "admin" && <AdminPanel />}
    </div>
  );
}

export default Dashboard;Interval(checkStatus, 5000);
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
