from finflow.app import create_service_app

app = create_service_app("notification-service")


@app.get("/notifications", tags=["notifications"])
def notifications():
    return [{"title": "Fraud alert", "body": "High-risk transaction needs review.", "channel": "in_app", "read": False}]


@app.post("/notifications/send", tags=["notifications"])
def send_notification(user_id: str, title: str, body: str, channel: str = "email"):
    return {"user_id": user_id, "title": title, "channel": channel, "status": "queued"}

