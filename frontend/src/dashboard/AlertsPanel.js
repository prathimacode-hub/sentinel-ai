import React from "react";

function AlertsPanel({ alerts }) {
  return (
    <div className="alert-panel">
      <h3>🚨 Critical Alerts</h3>

      {alerts.length === 0 && <p>No critical alerts</p>}

      {alerts.map((alert, index) => (
        <div key={index} className="alert-item">
          <p><b>Level:</b> {alert.level}</p>
          <p><b>Score:</b> {alert.score}</p>
          <p>{alert.explanation}</p>
        </div>
      ))}
    </div>
  );
}

export default AlertsPanel;
