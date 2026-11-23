from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal
import json
import uuid
from sqlalchemy.orm import Session
from backend.app.models.receipt import Receipt, ReceiptLineItem
from backend.app.models.transaction import Transaction
from backend.app.ml.ocr_engine import ocr_engine, ExtractedReceiptData
from backend.app.services.audit_service import audit_service
from backend.app.services.transaction_service import transaction_service

class ReceiptService:
    @staticmethod
    def process_receipt_upload(
        db: Session,
        organization_id: str,
        user_id: str,
        file_bytes: bytes,
        filename: str,
        actor_email: Optional[str] = None
    ) -> Receipt:
        # 1. SHA-256 Duplicate Check
        f_hash = ocr_engine.compute_file_hash(file_bytes)
        existing = db.query(Receipt).filter(
            Receipt.organization_id == organization_id,
            Receipt.file_hash == f_hash
        ).first()
        if existing:
            raise ValueError(f"Duplicate receipt detected. This document was already uploaded on {existing.created_at.strftime('%Y-%m-%d')} (ID: {existing.id}).")

        # 2. Extract structured fields with OCR engine
        parsed: ExtractedReceiptData = ocr_engine.parse_document(file_bytes, filename)

        # 3. Create Receipt in UPLOADED / OCR_PROCESSED state
        rec = Receipt(
            organization_id=organization_id,
            user_id=user_id,
            file_name=filename,
            file_hash=f_hash,
            merchant_name=parsed.merchant_name,
            total_amount=Decimal(str(parsed.total_amount)) if parsed.total_amount else None,
            currency=parsed.currency,
            tax_amount=Decimal(str(parsed.tax_amount)) if parsed.tax_amount else None,
            invoice_number=parsed.invoice_number,
            receipt_date=datetime.now(timezone.utc),
            status="OCR_PROCESSED",
            raw_text=parsed.raw_text
        )
        db.add(rec)
        db.flush()

        # Add line items
        for item in parsed.line_items:
            db.add(ReceiptLineItem(
                receipt_id=rec.id,
                description=item.description,
                quantity=item.quantity,
                unit_price=Decimal(str(item.unit_price)),
                total_price=Decimal(str(item.total_price))
            ))

        audit_service.log_action(
            db=db,
            organization_id=organization_id,
            actor_id=user_id,
            actor_email=actor_email,
            action="RECEIPT_UPLOADED_AND_PARSED",
            resource_type="RECEIPT",
            resource_id=rec.id,
            metadata={"filename": filename, "merchant": parsed.merchant_name, "total": parsed.total_amount}
        )

        db.commit()
        db.refresh(rec)
        return rec

    @staticmethod
    def confirm_receipt_to_transaction(
        db: Session,
        receipt_id: str,
        merchant_name: str,
        total_amount: Decimal,
        category_id: Optional[str],
        user_id: str,
        actor_email: Optional[str]
    ) -> Transaction:
        rec = db.query(Receipt).filter(Receipt.id == receipt_id).first()
        if not rec:
            raise ValueError("Receipt not found.")

        # Update receipt values if user corrected them
        rec.merchant_name = merchant_name
        rec.total_amount = total_amount
        rec.category_id = category_id
        rec.status = "VERIFIED"

        # Create corresponding real transaction
        tx = transaction_service.create_transaction(
            db=db,
            organization_id=rec.organization_id,
            user_id=user_id,
            amount=total_amount,
            merchant_name=merchant_name,
            currency=rec.currency,
            description=f"Verified expense from receipt {rec.invoice_number or rec.file_name}",
            category_id=category_id,
            payment_method="RECEIPT_REIMBURSEMENT",
            actor_email=actor_email
        )

        rec.transaction_id = tx.id
        db.commit()
        db.refresh(rec)
        return tx

receipt_service = ReceiptService()
