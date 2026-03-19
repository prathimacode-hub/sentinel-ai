import axios from "axios";

// Create Axios instance
const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 10000,
});

// -----------------------------
// API CALL: Analyze Frame
// -----------------------------
export const analyzeFrame = async (imageBlob) => {
  try {
    const formData = new FormData();
    formData.append("file", imageBlob, "frame.jpg");

    const response = await API.post("/analyze-frame/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;

  } catch (error) {
    console.error("API Error:", error);
    return {
      score: { total_score: 0 },
      event: {
        level: "LOW",
        explanation: "API error"
      }
    };
  }
};

// -----------------------------
// HEALTH CHECK
// -----------------------------
export const checkBackendStatus = async () => {
  try {
    const res = await API.get("/");
    return res.data;
  } catch (err) {
    return { status: "offline" };
  }
};
