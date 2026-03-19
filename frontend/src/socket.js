const SOCKET_URL = "ws://127.0.0.1:8000/ws";

let socket = null;

export const connectSocket = (onMessage) => {
  socket = new WebSocket(SOCKET_URL);

  socket.onopen = () => {
    console.log("WebSocket Connected");
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage(data);
  };

  socket.onerror = (error) => {
    console.error("WebSocket Error:", error);
  };

  socket.onclose = () => {
    console.log("WebSocket Disconnected");
  };
};

export const sendSocketMessage = (msg) => {
  if (socket) {
    socket.send(JSON.stringify(msg));
  }
};
