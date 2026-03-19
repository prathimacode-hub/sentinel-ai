import React, { useState } from "react";

function AdminPanel() {
  const [threshold, setThreshold] = useState(60);

  return (
    <div className="analytics">
      <h2>🛠 Admin Control Panel</h2>

      <div className="tile">
        <h3>Alert Threshold</h3>
        <input
          type="range"
          min="10"
          max="100"
          value={threshold}
          onChange={(e) => setThreshold(e.target.value)}
        />
        <p>Current Threshold: {threshold}</p>
      </div>

      <div className="tile">
        <h3>System Controls</h3>
        <button>Start Monitoring</button>
        <button>Stop Monitoring</button>
      </div>
    </div>
  );
}

export default AdminPanel;
