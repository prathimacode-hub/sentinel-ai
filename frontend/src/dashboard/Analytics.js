import React from "react";

function Analytics({ events }) {

  const total = events.length;
  const high = events.filter(e => e.level === "HIGH").length;
  const medium = events.filter(e => e.level === "MEDIUM").length;

  return (
    <div className="analytics">
      <h2>📊 Analytics Dashboard</h2>

      <div className="grid">
        <div className="tile">
          <h3>Total Events</h3>
          <p>{total}</p>
        </div>

        <div className="tile">
          <h3>High Alerts</h3>
          <p>{high}</p>
        </div>

        <div className="tile">
          <h3>Medium Alerts</h3>
          <p>{medium}</p>
        </div>
      </div>

      <div className="tile">
        <h3>Trend Insight</h3>
        <p>
          {high > medium
            ? "⚠ High cheating risk detected"
            : "✅ System stable"}
        </p>
      </div>
    </div>
  );
}

export default Analytics;
