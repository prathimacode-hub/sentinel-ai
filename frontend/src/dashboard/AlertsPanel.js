import React from "react";

function AlertsPanel({ alerts }) {
  return (
    <div className="alert-panel">
      <h3>🚨 Critical Alerts</h3>

      {alerts.map((alert, index) => (
        <div key={index} className="alert-item high-alert">
          <p><b>⚠ {alert.level}</b> | Score: {alert.score}</p>
          <p>{alert.explanation}</p>
        </div>
      ))}
    </div>
  );
}

export default AlertsPanel;;
