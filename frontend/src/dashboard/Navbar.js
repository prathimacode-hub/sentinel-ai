import React from "react";

function Navbar({ setMode }) {
  return (
    <div className="navbar">
      <h1>SentinelAI 🎯</h1>

      <div>
        <button onClick={() => setMode("live")}>Live</button>
        <button onClick={() => setMode("analytics")}>Analytics</button>
        <button onClick={() => setMode("admin")}>Admin</button>
      </div>
    </div>
  );
}

export default Navbar;
