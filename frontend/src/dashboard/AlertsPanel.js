import React, { useEffect, useRef } from "react";

function AlertsPanel({ alerts }) {
  const lastAlertRef = useRef(null);

  const playAlertSound = () => {
    const audio = new Audio("/alert.mp3");
    audio.play().catch(() => {
      // Prevent browser autoplay errors
    });
  };

  useEffect(() => {
    if (alerts.length === 0) return;

    const latestAlert = alerts[0];

    // Avoid playing sound repeatedly for same alert
    if (
      latestAlert.level === "HIGH" &&
      latestAlert !== lastAlertRef.current
    ) {
      playAlertSound();
      lastAlertRef.current = latestAlert;
    }
  }, [alerts]);

  return (
    <div className="alert-panel">
      <h3>🚨 Critical Alerts</h3>

      {alerts.map((alert, index) => (
        <div
          key={index}
          className={`alert-item ${
            alert.level === "HIGH" ? "high-alert" : "medium-alert"
          }`}
        >
          <p>
            <b>⚠ {alert.level}</b> | Score: {alert.score}
          </p>
          <p>{alert.explanation}</p>
        </div>
      ))}
    </div>
  );
}

export default AlertsPanel;
