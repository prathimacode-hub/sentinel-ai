from datetime import datetime
from typing import List
from fastapi import WebSocket

# -----------------------------------
# GLOBAL WEBSOCKET CLIENT MANAGER
# -----------------------------------

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"❌ Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """
        Send message to all connected clients
        """
        disconnected_clients = []

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected_clients.append(connection)

        # Clean up dead connections
        for conn in disconnected_clients:
            self.disconnect(conn)


# Create global manager instance
manager = ConnectionManager()


# -----------------------------------
# ALERT FUNCTIONS
# -----------------------------------

def send_alert(event: dict):
    """
    Console + structured alert log
    """
    timestamp = datetime.utcnow().isoformat()

    alert_data = {
        "timestamp": timestamp,
        "level": event.get("level"),
        "score": event.get("score"),
        "message": event.get("explanation"),
        "reasons": event.get("reasons", [])
    }

    print("\n🚨 ALERT TRIGGERED 🚨")
    print(alert_data)

    return alert_data


async def broadcast_alert(event: dict):
    """
    Send alert to frontend via WebSocket
    """
    message = {
        "type": "ALERT",
        "data": event
    }

    await manager.broadcast(message)


# -----------------------------------
# OPTIONAL: FUTURE EXTENSIONS
# -----------------------------------

def send_email_alert(event: dict):
    """
    Placeholder for email alerts
    """
    pass


def send_sms_alert(event: dict):
    """
    Placeholder for SMS alerts
    """
    pass


def log_alert(event):
    """
    Log alerts separately (optional)
    """
    print(f"[LOG] {event}")
}")
