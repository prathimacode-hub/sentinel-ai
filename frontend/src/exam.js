// frontend/src/exam.js

export function initStudentMonitoring({ feedId, overlayId, wsUrl, demoMode = true }) {
  const feed = document.getElementById(feedId);
  const overlay = document.getElementById(overlayId);

  if (!feed || !overlay) {
    console.error("❌ Feed or Overlay element not found");
    return;
  }

  // -----------------------------
  // LOCK VIDEO FEED
  // -----------------------------
  feed.oncontextmenu = () => false;
  feed.ondragstart = () => false;

  // -----------------------------
  // START WEBCAM
  // -----------------------------
  async function startWebcam() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
      feed.srcObject = stream;
    } catch (err) {
      console.error("⚠ Webcam not accessible:", err);
      alert("Cannot access webcam. Please allow camera permissions.");
    }
  }
  startWebcam();

  // -----------------------------
  // ALERT SOUND
  // -----------------------------
  const alertSound = new Audio("/alert.mp3");

  // -----------------------------
  // WEBSOCKET CONNECTION
  // -----------------------------
  let socket;
  function connectWebSocket() {
    socket = new WebSocket(wsUrl);

    socket.onopen = () => console.log("✅ WebSocket Connected");

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // ALERT
        if (data.type === "ALERT") {
          overlay.textContent = `⚠️ Alert: ${data.level || "Suspicious"}!`;
          overlay.classList.add("alert-flash");

          if (data.level === "HIGH") {
            alertSound.play().catch(() => {});
          }

          setTimeout(() => {
            overlay.textContent = "Monitoring Active ✅";
            overlay.classList.remove("alert-flash");
          }, 4000);
        }

        // LIVE FRAME
        if (data.type === "LIVE_FRAME" && data.frame) {
          const img = new Image();
          img.src = `data:image/jpeg;base64,${data.frame}`;
          const canvas = document.createElement("canvas");
          canvas.width = 640;
          canvas.height = 480;
          const ctx = canvas.getContext("2d");
          img.onload = () => ctx.drawImage(img, 0, 0, 640, 480);
          feed.srcObject = canvas.captureStream();
        }

      } catch (err) {
        console.error("⚠ WebSocket Message Error:", err);
      }
    };

    socket.onerror = (err) => console.error("⚠ WebSocket Error:", err);

    socket.onclose = () => {
      console.log("🔴 WebSocket Disconnected, retrying in 3s...");
      setTimeout(connectWebSocket, 3000);
    };
  }
  connectWebSocket();

  // -----------------------------
  // DEMO MODE ALERTS
  // -----------------------------
  if (demoMode) {
    setInterval(() => {
      if (Math.random() > 0.85) {
        overlay.textContent = "⚠️ Alert Detected!";
        overlay.classList.add("alert-flash");
        setTimeout(() => {
          overlay.textContent = "Monitoring Active ✅";
          overlay.classList.remove("alert-flash");
        }, 3000);
      }
    }, 5000);

    // Optional: simulate webcam frames
    const demoFrames = [];
    for (let i = 1; i <= 5; i++) {
      fetch(`/student_database/student_${i}.jpg`)
        .then(res => res.blob())
        .then(blob => {
          const reader = new FileReader();
          reader.onload = () => demoFrames.push(reader.result);
          reader.readAsDataURL(blob);
        });
    }

    setInterval(() => {
      if (demoFrames.length === 0) return;
      const randomFrame = demoFrames[Math.floor(Math.random() * demoFrames.length)];
      const canvas = document.createElement("canvas");
      canvas.width = 640;
      canvas.height = 480;
      const ctx = canvas.getContext("2d");
      const img = new Image();
      img.src = randomFrame;
      img.onload = () => {
        ctx.drawImage(img, 0, 0, 640, 480);
        feed.srcObject = canvas.captureStream();
      };
    }, 1000);
  }
}