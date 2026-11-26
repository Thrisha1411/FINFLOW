from uuid import UUID
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from finflow.app import create_service_app
from finflow.database import get_db
from finflow.domain_services import FraudEngine, PaymentWorkflowService
from finflow.repositories import TransactionRepository
from finflow.schemas import StatusUpdate, TransactionCreate, TransactionRead
from finflow.security import TokenPrincipal, current_principal
from finflow import models

app = create_service_app("payment-service")


@app.post("/transactions", response_model=TransactionRead, tags=["transactions"])
def create_transaction(payload: TransactionCreate, principal: TokenPrincipal = Depends(current_principal), db: Session = Depends(get_db)):
    org = principal.organization_id or "demo-org"
    return PaymentWorkflowService(TransactionRepository(db), FraudEngine()).create(principal.sub, org, payload)


@app.get("/transactions", response_model=list[TransactionRead], tags=["transactions"])
def list_transactions(principal: TokenPrincipal = Depends(current_principal), db: Session = Depends(get_db)):
    return TransactionRepository(db).list(principal.organization_id or "demo-org")


@app.patch("/transactions/{transaction_id}/status", response_model=TransactionRead, tags=["transactions"])
def update_status(transaction_id: UUID, payload: StatusUpdate, principal: TokenPrincipal = Depends(current_principal), db: Session = Depends(get_db)):
    repo = TransactionRepository(db)
    transaction = repo.get(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return repo.update_status(transaction, payload.status, principal.sub, payload.reason)


@app.post("/transactions/{transaction_id}/refund", tags=["transactions"])
def refund(transaction_id: UUID):
    return {"transaction_id": str(transaction_id), "currency": "INR", "status": models.TransactionStatus.processing.value, "message": "Refund queued"}

@app.get("/transactions/export.csv", tags=["transactions"])
def export_transactions():
    return {"download_url": "/exports/transactions/latest.csv"}
