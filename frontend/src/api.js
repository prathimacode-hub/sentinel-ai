// frontend/src/api.js
import axios from "axios";

// -----------------------------
// BASE URL
// -----------------------------
const BASE_URL = "http://127.0.0.1:8000";

// -----------------------------
// AXIOS INSTANCE
// -----------------------------
const API = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
});

// -----------------------------
// REQUEST INTERCEPTOR (TOKEN)
// -----------------------------
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (!config.headers) config.headers = {};
  if (token) config.headers["Authorization"] = `Bearer ${token}`;
  return config;
});

// -----------------------------
// RESPONSE INTERCEPTOR
// -----------------------------
API.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("⚠ API Error:", error?.response?.data || error.message);
    return Promise.reject(error);
  }
);

// -----------------------------
// SAFE ERROR HANDLER
// -----------------------------
const safe = async (fn, fallback) => {
  try {
    const res = await fn();
    return res.data;
  } catch (err) {
    console.warn("API fallback:", err.message);
    return fallback;
  }
};

// -----------------------------
// BACKEND ROOT CHECK
// -----------------------------
export const pingBackend = async () =>
  safe(() => API.get("/"), { status: "offline" });

// -----------------------------
// HEALTH
// -----------------------------
export const checkBackendStatus = async () =>
  safe(() => API.get("/status"), { monitoring: false });

// -----------------------------
// LOGIN
// -----------------------------
export const login = async (username, role) => {
  try {
    const res = await API.post("/login", { username, role });
    localStorage.setItem("access_token", res.data.access_token);
    localStorage.setItem("refresh_token", res.data.refresh_token);
    return res.data;
  } catch (err) {
    console.error(err);
    return { status: "failed" };
  }
};

// -----------------------------
// REFRESH TOKEN
// -----------------------------
export const refreshToken = async () => {
  const refresh_token = localStorage.getItem("refresh_token");
  if (!refresh_token) return;
  const res = await API.post("/refresh", { refresh_token });
  localStorage.setItem("access_token", res.data.access_token);
};

// -----------------------------
// ANALYZE FRAME
// -----------------------------
export const analyzeFrame = async (imageBlob, studentId, cameraId = null) => {
  try {
    const formData = new FormData();
    formData.append("file", imageBlob, "frame.jpg");

    const res = await API.post(`/analyze-frame/${studentId}`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });

    return res.data;
  } catch (error) {
    return {
      score: 0,
      risk_level: "LOW",
      events: [],
      explanation: "Backend not reachable",
      image: null,
    };
  }
};

// -----------------------------
// CAMERA REGISTRY
// -----------------------------
export const fetchCameraRegistry = async () => {
  try {
    const res = await API.get("/config/camera_registry.json");
    return res.data;
  } catch (err) {
    console.warn("Using simulated camera registry");

    // fallback simulation for 30 students only
    const students = Array.from({ length: 30 }, (_, i) => ({
      student_id: `student_${i + 1}`,
      camera_id: `sim_cam_${i + 1}`,
    }));

    return { students, hall_cctv: [] };
  }
};

// -----------------------------
// EVENTS
// -----------------------------
export const fetchEvents = async () => safe(() => API.get("/events"), []);

// -----------------------------
// SESSIONS
// -----------------------------
export const fetchSessions = async () => safe(() => API.get("/sessions"), []);

// -----------------------------
// ANALYTICS
// -----------------------------
export const fetchAnalytics = async () =>
  safe(() => API.get("/analytics"), {
    total_events: 0,
    high_risk: 0,
    medium_risk: 0,
    low_risk: 0,
  });

// -----------------------------
// EVIDENCE URL
// -----------------------------
export const getEvidenceUrl = (filename) => {
  if (!filename) return ""; // no placeholder
  return `${BASE_URL}/evidence/${filename}`;
};

// -----------------------------
// START MONITORING
// -----------------------------
export const startMonitoring = async () =>
  safe(() => API.post("/start-monitoring"), { status: "failed" });

// -----------------------------
// STOP MONITORING
// -----------------------------
export const stopMonitoring = async () =>
  safe(() => API.post("/stop-monitoring"), { status: "failed" });

// -----------------------------
// RESET EVENTS
// -----------------------------
export const resetEvents = async () =>
  safe(() => API.post("/reset-events"), { status: "failed" });

// -----------------------------
// EVIDENCE LOG
// -----------------------------
export const fetchEvidenceLog = async () => safe(() => API.get("/evidence-log"), []);

// -----------------------------
// SYSTEM STATUS
// -----------------------------
export const getSystemStatus = async () =>
  safe(() => API.get("/status"), { monitoring: false, websockets: 0 });

export default API;