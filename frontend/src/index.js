import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles.css";

// -----------------------------
// ERROR BOUNDARY
// -----------------------------
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error("App Crash:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: "40px",
          textAlign: "center",
          fontFamily: "Arial",
          color: "#f87171"
        }}>
          <h1>⚠ SentinelAI Dashboard Crashed</h1>
          <p>Something went wrong. Please restart the app.</p>
        </div>
      );
    }

    return this.props.children;
  }
}

// -----------------------------
// ROOT INITIALIZATION
// -----------------------------
const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Root container missing in index.html");
}

const root = ReactDOM.createRoot(rootElement);

// -----------------------------
// RENDER APP
// -----------------------------
root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);