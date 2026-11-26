from enum import StrEnum
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from uuid import uuid4
import json


class EventType(StrEnum):
    transaction_created = "Transaction Created"
    transaction_flagged = "Transaction Flagged"
    fraud_detected = "Fraud Detected"
    subscription_renewed = "Subscription Renewed"
    budget_alert_triggered = "Budget Alert Triggered"


class DomainEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: EventType
    aggregate_id: str
    organization_id: str | None = None
    payload: dict
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_json(self) -> str:
        return self.model_dump_json()


class EventPublisher:
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers

    async def publish(self, topic: str, event: DomainEvent) -> None:
        try:
            from aiokafka import AIOKafkaProducer
            producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
            await producer.start()
            try:
                await producer.send_and_wait(topic, event.to_json().encode("utf-8"))
            finally:
                await producer.stop()
        except Exception:
            print(json.dumps({"level": "warning", "message": "event_publish_failed", "topic": topic, "event": event.model_dump(mode="json")}))

