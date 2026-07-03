from celery import Celery
from .config import get_settings
from .domain_services import AssistantService, FraudEngine, ForecastService
from .schemas import FraudSignal

settings = get_settings()
celery_app = Celery("finflow", broker=settings.redis_url, backend=settings.redis_url)


@celery_app.task(name="receipt.process")
def process_receipt(raw_text: str) -> dict:
    return AssistantService().extract_receipt(raw_text)


@celery_app.task(name="fraud.scan")
def fraud_scan(payload: dict) -> dict:
    return FraudEngine().score(FraudSignal(**payload)).model_dump()


@celery_app.task(name="forecast.generate")
def generate_forecast(amounts: list[float]) -> dict:
    return ForecastService().spend_projection(amounts)


@celery_app.task(name="email.deliver")
def deliver_email(to_email: str, subject: str, body: str) -> dict:
    return {"to": to_email, "subject": subject, "status": "queued"}

