from fastapi import UploadFile, File
from finflow.app import create_service_app
from finflow.domain_services import AssistantService, FraudEngine
from finflow.schemas import AssistantAnswer, AssistantQuestion, ReceiptExtraction

app = create_service_app("ai-assistant-service")


@app.post("/assistant/chat", response_model=AssistantAnswer, tags=["ai"])
def chat(payload: AssistantQuestion):
    return AssistantAnswer(answer=AssistantService().answer(payload.question), sources=["transactions", "fraud_cases", "budgets"])


@app.post("/assistant/receipt", response_model=ReceiptExtraction, tags=["ai"])
async def receipt(file: UploadFile = File(...)):
    raw = (await file.read()).decode("utf-8", errors="ignore")
    return ReceiptExtraction(**AssistantService().extract_receipt(raw))


@app.post("/assistant/categorize", tags=["ai"])
def categorize(merchant: str, memo: str = ""):
    return {"category": FraudEngine().categorize(merchant, memo)}

