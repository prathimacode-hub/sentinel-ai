// src/socket.js

// -----------------------------
// CONFIG
// -----------------------------
const DASHBOARD_WS_URL = "ws://127.0.0.1:8000/ws/dashboard";
const STUDENT_WS_URL = "ws://127.0.0.1:8000/ws/student";

let socket = null;
let subscribers = [];
let reconnectInterval = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 10;
let connectionStatus = "disconnected";

// -----------------------------
// DEMO MODE SIMULATION
// -----------------------------
let demoMode = true;
let demoFrames = [];

// preload demo frames
if (demoMode) {
  for (let i = 1; i <= 5; i++) {
    fetch(`/student_database/student_${i}.jpg`)
      .then(res => res.blob())
      .then(blob => {
        const reader = new FileReader();
        reader.onload = () => demoFrames.push(reader.result);
        reader.readAsDataURL(blob);
      });
  }

  // simulate live frames and alerts
  setInterval(() => {
    if (!demoMode || demoFrames.length === 0) return;

    for (let i = 1; i <= 30; i++) {
      const frame = demoFrames[Math.floor(Math.random() * demoFrames.length)];
      const data = {
        type: "LIVE_FRAME",
        student_id: `student_${i}`,
        frame,
      };
      subscribers.forEach(cb => cb(data));
    }

    // simulate random alerts
    const alertTypes = ["multiple_faces", "gaze_deviation", "unauthorized_object", "background_speech"];
    const riskLevels = ["LOW", "MEDIUM", "HIGH"];
    const randomStudent = Math.floor(Math.random() * 30) + 1;

    const alert = {
      type: "ALERT",
      data: {
        student_id: `student_${randomStudent}`,
        risk_level: riskLevels[Math.floor(Math.random() * riskLevels.length)],
        events: [{ type: alertTypes[Math.floor(Math.random() * alertTypes.length)] }],
        timestamp: new Date().toISOString(),
        image: demoFrames[Math.floor(Math.random() * demoFrames.length)]
      }
    };
    subscribers.forEach(cb => cb(alert));

  }, 5000); // every 5 seconds
}

// -----------------------------
// CONNECT SOCKET
// -----------------------------
export const connectSocket = (listener, endpoint = "dashboard") => {
  const url = endpoint === "student" ? STUDENT_WS_URL : DASHBOARD_WS_URL;

  if (socket && socket.readyState === WebSocket.OPEN) {
    if (listener) subscribers.push(listener);
    return;
  }

  socket = new WebSocket(url);
  connectionStatus = "connecting";

  socket.onopen = () => {
    console.log(`✅ WebSocket Connected (${endpoint})`);
    connectionStatus = "connected";
    reconnectAttempts = 0;

    if (reconnectInterval) {
      clearInterval(reconnectInterval);
      reconnectInterval = null;
    }
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      subscribers.forEach(cb => {
        if (typeof cb === "function") cb(data);
      });
    } catch (err) {
      console.error("⚠ Invalid WebSocket message", err);
    }
  };

  socket.onerror = (error) => {
    console.error("⚠ WebSocket Error:", error);
  };

  socket.onclose = () => {
    console.log(`🔴 WebSocket Disconnected (${endpoint})`);
    connectionStatus = "disconnected";
    startReconnect(endpoint);
  };

  if (listener && typeof listener === "function") {
    subscribers.push(listener);
  }
};

// -----------------------------
// RECONNECT LOGIC
// -----------------------------
const startReconnect = (endpoint) => {
  if (reconnectInterval) return;

  reconnectInterval = setInterval(() => {
    if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      console.log("❌ Max reconnect attempts reached");
      clearInterval(reconnectInterval);
      return;
    }

    reconnectAttempts++;
    console.log(`🔁 Reconnecting... Attempt ${reconnectAttempts}`);
    connectSocket(null, endpoint);

  }, 3000);
};

// -----------------------------
// SEND MESSAGE
// -----------------------------
export const sendSocketMessage = (msg) => {
  if (!socket) return console.warn("⚠ Socket not initialized");

  if (socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(msg));
  } else {
    console.warn("⚠ Socket not connected");
  }
};

// -----------------------------
// UNSUBSCRIBE / CLOSE
// -----------------------------
export const unsubscribe = (listener) => {
  if (listener) {
    subscribers = subscribers.filter(cb => cb !== listener);
  } else if (socket) {
    socket.close();
    socket = null;
    subscribers = [];
    connectionStatus = "disconnected";
  }
};

// -----------------------------
// GET CONNECTION STATUS
// -----------------------------
export const getSocketStatus = () => connectionStatus;

// -----------------------------
// HEARTBEAT (Optional ping)
// -----------------------------
export const startHeartbeat = (interval = 10000) => {
  setInterval(() => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: "ping" }));
    }
  }, interval);
};