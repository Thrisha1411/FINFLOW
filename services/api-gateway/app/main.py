from collections import defaultdict
from time import time
import httpx
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from finflow.app import create_service_app

app: FastAPI = create_service_app("api-gateway")
rate_bucket: dict[str, list[float]] = defaultdict(list)
routes = {
    "auth": "http://auth-service:8000",
    "transactions": "http://payment-service:8000",
    "fraud": "http://fraud-service:8000",
    "analytics": "http://analytics-service:8000",
    "assistant": "http://ai-assistant-service:8000",
    "subscriptions": "http://subscription-service:8000",
    "notifications": "http://notification-service:8000",
    "audit": "http://audit-service:8000",
}
connections: set[WebSocket] = set()


@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(service: str, path: str, request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time()
    rate_bucket[ip] = [stamp for stamp in rate_bucket[ip] if now - stamp < 60]
    if len(rate_bucket[ip]) > 120:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    rate_bucket[ip].append(now)
    upstream = routes.get(service)
    if not upstream:
        raise HTTPException(status_code=404, detail="Unknown service")
    body = await request.body()
    async with httpx.AsyncClient(timeout=30) as client:
        upstream_response = await client.request(
            request.method,
            f"{upstream}/{service}/{path}" if path else f"{upstream}/{service}",
            content=body,
            params=request.query_params,
            headers={k: v for k, v in request.headers.items() if k.lower() != "host"},
        )
    return Response(content=upstream_response.content, status_code=upstream_response.status_code, media_type=upstream_response.headers.get("content-type"))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.add(websocket)
    try:
        while True:
            message = await websocket.receive_json()
            await websocket.send_json({"type": "ack", "message": message})
    except WebSocketDisconnect:
        connections.remove(websocket)

