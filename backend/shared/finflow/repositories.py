from collections.abc import Sequence
from uuid import UUID
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from . import models


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> models.User | None:
        return self.db.scalar(select(models.User).where(models.User.email == email))

    def add(self, user: models.User) -> models.User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, transaction: models.Transaction) -> models.Transaction:
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def list(self, organization_id: str, limit: int = 100) -> Sequence[models.Transaction]:
        return self.db.scalars(
            select(models.Transaction)
            .where(models.Transaction.organization_id == organization_id)
            .order_by(desc(models.Transaction.created_at))
            .limit(limit)
        ).all()

    def get(self, transaction_id: UUID) -> models.Transaction | None:
        return self.db.get(models.Transaction, transaction_id)

    def update_status(self, transaction: models.Transaction, status: models.TransactionStatus, actor_id: str | None, reason: str | None) -> models.Transaction:
        previous = transaction.status
        transaction.status = status
        self.db.add(models.TransactionEvent(transaction_id=transaction.id, from_status=previous.value, to_status=status.value, actor_id=actor_id, reason=reason))
        self.db.commit()
        self.db.refresh(transaction)
        return transaction


class FraudRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_case(self, case: models.FraudCase) -> models.FraudCase:
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        return case

    def list_cases(self, organization_id: str) -> Sequence[models.FraudCase]:
        return self.db.scalars(select(models.FraudCase).where(models.FraudCase.organization_id == organization_id).order_by(desc(models.FraudCase.created_at))).all()


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, log: models.AuditLog) -> models.AuditLog:
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def search(self, organization_id: str | None, q: str | None = None) -> Sequence[models.AuditLog]:
        stmt = select(models.AuditLog).order_by(desc(models.AuditLog.created_at)).limit(200)
        if organization_id:
            stmt = stmt.where(models.AuditLog.organization_id == organization_id)
        if q:
            stmt = stmt.where(models.AuditLog.action.ilike(f"%{q}%"))
        return self.db.scalars(stmt).all()

