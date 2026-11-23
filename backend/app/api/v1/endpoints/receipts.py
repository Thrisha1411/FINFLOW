from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user, CurrentUserContext
from backend.app.models.receipt import Receipt
from backend.app.schemas.receipt import ReceiptResponse, ReceiptConfirmRequest
from backend.app.schemas.transaction import TransactionResponse
from backend.app.services.receipt_service import receipt_service

router = APIRouter()

@router.post("/upload", response_model=ReceiptResponse)
async def upload_receipt(
    file: UploadFile = File(...),
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 10MB limit.")

    try:
        receipt = receipt_service.process_receipt_upload(
            db=db,
            organization_id=ctx.organization_id,
            user_id=ctx.user_id,
            file_bytes=content,
            filename=file.filename or "receipt.pdf",
            actor_email=ctx.email
        )
        return receipt
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("", response_model=List[ReceiptResponse])
def list_receipts(
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Receipt).filter(
        Receipt.organization_id == ctx.organization_id
    ).order_by(Receipt.created_at.desc()).all()

@router.post("/confirm", response_model=TransactionResponse)
def confirm_receipt(
    data: ReceiptConfirmRequest,
    ctx: CurrentUserContext = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        tx = receipt_service.confirm_receipt_to_transaction(
            db=db,
            receipt_id=data.receipt_id,
            merchant_name=data.merchant_name,
            total_amount=Decimal(str(data.total_amount)),
            category_id=data.category_id,
            user_id=ctx.user_id,
            actor_email=ctx.email
        )
        return tx
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
