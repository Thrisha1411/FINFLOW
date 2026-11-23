"""
OCR Document Parser & Structured Receipt/Invoice Extractor.
Extracts merchant, transaction date, total amount, currency, tax, invoice number,
and line items with Pydantic validation and duplicate SHA-256 detection.
"""

from typing import Dict, Any, List, Optional
from decimal import Decimal
import hashlib
import re
from datetime import datetime
from pydantic import BaseModel, Field

class ExtractedLineItem(BaseModel):
    description: str
    quantity: int = 1
    unit_price: float
    total_price: float

class ExtractedReceiptData(BaseModel):
    merchant_name: str
    total_amount: float
    currency: str = "USD"
    tax_amount: Optional[float] = None
    invoice_number: Optional[str] = None
    receipt_date: Optional[str] = None
    suggested_category: str = "Other"
    line_items: List[ExtractedLineItem] = Field(default_factory=list)
    confidence: float = 0.85
    raw_text: str = ""

class OCREngine:
    @staticmethod
    def compute_file_hash(content_bytes: bytes) -> str:
        """Computes SHA-256 hash for duplicate receipt detection."""
        return hashlib.sha256(content_bytes).hexdigest()

    @classmethod
    def parse_document(cls, file_bytes: bytes, filename: str) -> ExtractedReceiptData:
        """
        Extracts structured fields from PDF or text/image file.
        """
        extracted_text = ""
        if filename.lower().endswith(".pdf"):
            try:
                import fitz
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                for page in doc:
                    extracted_text += page.get_text() + "\n"
            except Exception:
                extracted_text = file_bytes.decode("utf-8", errors="ignore")
        else:
            extracted_text = file_bytes.decode("utf-8", errors="ignore")

        if not extracted_text.strip():
            extracted_text = f"Merchant: Expense Vendor\nDate: {datetime.utcnow().strftime('%Y-%m-%d')}\nTotal: $0.00"

        return cls._extract_structured_fields(extracted_text, filename)

    @staticmethod
    def _extract_structured_fields(text: str, filename: str) -> ExtractedReceiptData:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        # 1. Merchant Name
        merchant_name = "Unknown Vendor"
        for line in lines[:5]:
            cleaned = re.sub(r'[^a-zA-Z0-9\s&]', '', line).strip()
            if len(cleaned) > 2 and not any(kw in cleaned.lower() for kw in ["invoice", "receipt", "tax", "tel", "date", "total"]):
                merchant_name = cleaned
                break

        # Currency detection
        currency = "USD"
        if "€" in text or "EUR" in text:
            currency = "EUR"
        elif "£" in text or "GBP" in text:
            currency = "GBP"
        elif "₹" in text or "INR" in text:
            currency = "INR"

        # 2. Total Amount
        total_amount = 0.0
        # Pattern handles: Total: $84.20, Total: USD 84.20, Total 84.20, Due: 84.20
        amt_matches = re.findall(
            r'(?:total|amount|due|balance|subtotal)[\s:]*(?:usd|eur|gbp|inr|[\$€£₹])?\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)',
            text,
            re.IGNORECASE
        )
        if amt_matches:
            try:
                total_amount = float(amt_matches[-1].replace(",", ""))
            except ValueError:
                pass
        
        if total_amount == 0.0:
            all_numbers = re.findall(r'(?:usd|eur|gbp|inr|[\$€£₹])\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{2})?)', text, re.IGNORECASE)
            if all_numbers:
                try:
                    num_floats = [float(n.replace(",", "")) for n in all_numbers]
                    total_amount = max(num_floats)
                except ValueError:
                    pass

        # 3. Tax Amount
        tax_amount = None
        tax_matches = re.findall(
            r'(?:tax|vat|gst)[\s:]*(?:usd|eur|gbp|inr|[\$€£₹])?\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)',
            text,
            re.IGNORECASE
        )
        if tax_matches:
            try:
                tax_amount = float(tax_matches[0].replace(",", ""))
            except ValueError:
                pass

        # 4. Invoice Number
        invoice_number = None
        inv_matches = re.findall(r'(?:invoice|inv|receipt|bill)\s*(?:no|num|#)?[\s:]*([a-zA-Z0-9\-_]{4,25})', text, re.IGNORECASE)
        if inv_matches:
            invoice_number = inv_matches[0]

        # 5. Receipt Date
        receipt_date = None
        date_matches = re.findall(r'(\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})', text)
        if date_matches:
            receipt_date = date_matches[0]

        # 6. Line items
        line_items = []
        for line in lines:
            item_match = re.search(r'^(.*?)\s+(?:usd|eur|gbp|inr|[\$€£₹])?\s*([0-9]+\.[0-9]{2})$', line, re.IGNORECASE)
            if item_match and not any(k in item_match.group(1).lower() for k in ["total", "subtotal", "tax", "balance", "due"]):
                desc = item_match.group(1).strip()
                try:
                    price = float(item_match.group(2))
                    if len(desc) > 2 and price > 0:
                        line_items.append(ExtractedLineItem(
                            description=desc,
                            quantity=1,
                            unit_price=price,
                            total_price=price
                        ))
                except ValueError:
                    pass

        if not line_items and total_amount > 0:
            line_items.append(ExtractedLineItem(
                description=f"Transaction item at {merchant_name}",
                quantity=1,
                unit_price=total_amount,
                total_price=total_amount
            ))

        from backend.app.ml.categorizer import categorizer
        cat_result = categorizer.classify(merchant_name, text)

        return ExtractedReceiptData(
            merchant_name=merchant_name,
            total_amount=total_amount,
            currency=currency,
            tax_amount=tax_amount,
            invoice_number=invoice_number,
            receipt_date=receipt_date,
            suggested_category=cat_result["category"],
            line_items=line_items,
            confidence=0.90 if total_amount > 0 else 0.40,
            raw_text=text[:3000]
        )

ocr_engine = OCREngine()
