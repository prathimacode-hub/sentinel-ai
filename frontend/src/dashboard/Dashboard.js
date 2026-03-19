import React, { useState, useEffect, useRef } from "react";
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
  const [highlightId, setHighlightId] = useState(null);

  const alertSound = useRef(new Audio("/alert.mp3"));

  useEffect(() => {
    connectSocket((data) => {
      if (data.type === "ALERT") {
        const event = data.data;

        setAlerts((prev) => [event, ...prev]);
        setEvents((prev) => [event, ...prev]);

        // 🔊 PLAY SOUND
        alertSound.current.play().catch(() => {});

        // 🎯 Highlight student
        if (event.student_id) {
          setHighlightId(event.student_id);

          setTimeout(() => {
            setHighlightId(null);
          }, 5000);
        }
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
              <StudentTile
                key={id}
                id={id}
                highlight={highlightId === id}
              />
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

export default Dashboard;
