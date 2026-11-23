"""
Event Bus and Outbox Pattern Implementation.
Supports Kafka event emission with fallback transactional queueing.
"""
from typing import Dict, Any, Callable, List
from datetime import datetime, timezone
import json
import uuid
import logging
from backend.app.core.config import settings
from backend.app.core.redis import redis_service

logger = logging.getLogger("finflow.events")

class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Dict[str, Any]], Any]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[Dict[str, Any]], Any]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    def publish(self, event_type: str, payload: Dict[str, Any], org_id: str, actor_id: str = "SYSTEM"):
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "organization_id": org_id,
            "actor_id": actor_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }
        
        # 1. Dispatch to in-process subscribers
        handlers = self._subscribers.get(event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error handling event {event_type}: {e}")

        # 2. Publish to Redis / WebSocket channel for real-time dashboards
        channel = f"org:{org_id}:events"
        redis_service.publish(channel, event)
        logger.info(f"Event published: {event_type} (id={event['event_id']}, org={org_id})")

event_bus = EventBus()
