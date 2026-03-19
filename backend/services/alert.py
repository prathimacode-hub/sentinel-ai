import datetime

def send_alert(event):
    """
    Send alert for HIGH severity events
    """

    timestamp = datetime.datetime.utcnow().isoformat()

    alert_message = {
        "timestamp": timestamp,
        "level": event.get("level"),
        "score": event.get("score"),
        "message": event.get("explanation")
    }

    # Console alert (for hackathon demo)
    print("\n🚨 ALERT TRIGGERED 🚨")
    print(alert_message)

    # Future extensions:
    # - WebSocket push to dashboard
    # - Email alert
    # - SMS alert
    # - Push notification

    return alert_message


def send_realtime_alert(event, client_socket=None):
    """
    Optional: send alert to frontend via WebSocket
    """
    if client_socket:
        try:
            client_socket.send_json({
                "type": "ALERT",
                "data": event
            })
        except Exception as e:
            print("WebSocket Error:", str(e))


def log_alert(event):
    """
    Log alerts separately (optional)
    """
    print(f"[LOG] {event}")
