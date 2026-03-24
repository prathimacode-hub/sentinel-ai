import React, { useState, useEffect, useRef } from "react";

function Timeline({ events }) {
  const [latestEvents, setLatestEvents] = useState([]);
  const [riskFilter, setRiskFilter] = useState("");
  const [studentFilter, setStudentFilter] = useState("");
  const containerRef = useRef(null);
  const lastEventRef = useRef(null);

  // -----------------------------
  // UPDATE EVENTS
  // -----------------------------
  useEffect(() => {
    if (!events || events.length === 0) {
      setLatestEvents([]);
      return;
    }

    let updatedEvents = [...events];

    if (riskFilter) {
      updatedEvents = updatedEvents.filter((e) => e.level === riskFilter);
    }

    if (studentFilter) {
      updatedEvents = updatedEvents.filter(
        (e) => String(e.student_id) === studentFilter
      );
    }

    // Limit last 50 events
    updatedEvents = updatedEvents.slice(0, 50);

    setLatestEvents(updatedEvents);

    // Auto scroll to top for new events
    if (containerRef.current) {
      containerRef.current.scrollTop = 0;
    }

    // Play sound for HIGH events
    const latest = updatedEvents[0];
    if (latest && latest.level === "HIGH" && latest !== lastEventRef.current) {
      const audio = new Audio("/alert.mp3");
      audio.play().catch(() => {});
      lastEventRef.current = latest;
    }
  }, [events, riskFilter, studentFilter]);

  // -----------------------------
  // BORDER COLOR
  // -----------------------------
  const getBorderColor = (level) => {
    switch (level) {
      case "HIGH": return "#ef4444";
      case "MEDIUM": return "#f59e0b";
      case "LOW": return "#22c55e";
      default: return "#94a3b8";
    }
  };

  // -----------------------------
  // CLEAR TIMELINE
  // -----------------------------
  const clearTimeline = () => setLatestEvents([]);

  // -----------------------------
  // FORMAT TIME
  // -----------------------------
  const formatTime = (timestamp) => {
    if (!timestamp) return "N/A";
    try {
      return new Date(timestamp * 1000).toLocaleTimeString();
    } catch {
      return timestamp;
    }
  };

  // -----------------------------
  // UI
  // -----------------------------
  return (
    <div className="timeline">

      {/* HEADER */}
      <div style={{ display: "flex", justifyContent: "space-between", flexWrap: "wrap" }}>
        <h3>📊 Event Timeline</h3>
        <div style={{ display: "flex", gap: "5px", flexWrap: "wrap" }}>
          <select value={riskFilter} onChange={(e) => setRiskFilter(e.target.value)}>
            <option value="">All Risk</option>
            <option value="HIGH">HIGH</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="LOW">LOW</option>
          </select>

          <input
            placeholder="Student ID"
            value={studentFilter}
            onChange={(e) => setStudentFilter(e.target.value)}
          />

          <button onClick={clearTimeline}>🧹 Clear</button>
        </div>
      </div>

      {/* EMPTY */}
      {latestEvents.length === 0 && (
        <p style={{ color: "#94a3b8", fontStyle: "italic", marginTop: "10px" }}>
          No events recorded
        </p>
      )}

      {/* EVENTS */}
      <div ref={containerRef}>
        {latestEvents.map((event, index) => (
          <div
            key={index}
            className={`session-item ${event.level === "HIGH" ? "flash" : ""}`}
            style={{
              borderLeft: `4px solid ${getBorderColor(event.level)}`,
              paddingLeft: "10px",
              marginBottom: "10px",
              backgroundColor: event.level === "HIGH" ? "#2c1111" : "#334155",
              transition: "all 0.3s ease-in-out",
            }}
          >
            <p><b>🕒 Time:</b> {formatTime(event.timestamp)}</p>
            <p><b>🎓 Student:</b> {event.student_id || "N/A"}</p>
            <p><b>⚠ Level:</b> {event.level || "N/A"}</p>
            <p><b>📈 Score:</b> {event.score ?? 0}</p>
            <p>{event.explanation || event.message || "No details available"}</p>

            {/* Evidence */}
            {event.image && (
              <img
                src={`/evidence/${event.image}`}
                alt="Evidence"
                style={{
                  width: "100%",
                  maxWidth: "250px",
                  marginTop: "6px",
                  borderRadius: "6px",
                  border:
                    event.level === "HIGH"
                      ? "2px solid #ef4444"
                      : event.level === "MEDIUM"
                      ? "2px solid #ff9900"
                      : "2px solid #22c55e",
                  transition: "transform 0.2s ease, box-shadow 0.2s ease",
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = "scale(1.05)";
                  e.currentTarget.style.boxShadow = "0 0 15px #38bdf8";
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = "scale(1)";
                  e.currentTarget.style.boxShadow = "none";
                }}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Timeline;