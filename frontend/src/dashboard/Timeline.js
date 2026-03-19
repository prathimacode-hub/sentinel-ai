import React from "react";

function Timeline({ events }) {
  return (
    <div className="alert-panel">
      <h3>📊 Event Timeline</h3>

      {events.length === 0 && <p>No events recorded</p>}

      {events.slice(0, 10).map((event, index) => (
        <div key={index} className="alert-item">
          <p><b>Time:</b> {event.timestamp}</p>
          <p><b>Level:</b> {event.level}</p>
          <p>{event.explanation}</p>
        </div>
      ))}
    </div>
  );
}

export default Timeline;
