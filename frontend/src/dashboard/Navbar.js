import React from "react";

function Navbar({ status }) {
  return (
    <div className="navbar">
      <div>
        <h1>SentinelAI 🎯</h1>
        <p>AI Proctoring Dashboard</p>
      </div>

      <div>
        <span className={`status-indicator ${status}`}>
          Backend: {status.toUpperCase()}
        </span>
      </div>
    </div>
  );
}

export default Navbar;
