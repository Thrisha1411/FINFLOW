import json
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal, Base, engine
from backend.app.core.security import get_password_hash
from backend.app.core.totp import TOTPManager
from backend.app.models.organization import Organization, OrganizationMember, RoleEnum
from backend.app.models.user import User, UserSession
from backend.app.models.category import Category
from backend.app.models.transaction import Transaction, TransactionEvent
from backend.app.models.fraud import FraudCase, FraudSignal
from backend.app.models.receipt import Receipt, ReceiptLineItem
from backend.app.models.budget import Budget, BudgetCategory
from backend.app.models.subscription import Subscription
from backend.app.models.goal import FinancialGoal
from backend.app.models.audit import AuditLog
from backend.app.models.notification import Notification

DEFAULT_CATEGORIES = [
    {"name": "Food and Dining", "budget_group": "WANTS", "icon": "utensils", "color": "#f97316"},
    {"name": "Shopping", "budget_group": "WANTS", "icon": "shopping-bag", "color": "#ec4899"},
    {"name": "Transportation", "budget_group": "NEEDS", "icon": "car", "color": "#3b82f6"},
    {"name": "Healthcare", "budget_group": "NEEDS", "icon": "heart-pulse", "color": "#ef4444"},
    {"name": "Utilities", "budget_group": "NEEDS", "icon": "zap", "color": "#eab308"},
    {"name": "Rent", "budget_group": "NEEDS", "icon": "home", "color": "#6366f1"},
    {"name": "Entertainment", "budget_group": "WANTS", "icon": "film", "color": "#a855f7"},
    {"name": "Travel", "budget_group": "WANTS", "icon": "plane", "color": "#14b8a6"},
    {"name": "Education", "budget_group": "NEEDS", "icon": "book-open", "color": "#8b5cf6"},
    {"name": "Salary", "budget_group": "SAVINGS_INVESTMENTS", "icon": "wallet", "color": "#10b981"},
    {"name": "Investments", "budget_group": "SAVINGS_INVESTMENTS", "icon": "trending-up", "color": "#059669"},
    {"name": "Savings", "budget_group": "SAVINGS_INVESTMENTS", "icon": "piggy-bank", "color": "#047857"},
    {"name": "Insurance", "budget_group": "NEEDS", "icon": "shield-check", "color": "#0284c7"},
    {"name": "Business Expenses", "budget_group": "NEEDS", "icon": "briefcase", "color": "#475569"},
    {"name": "Other", "budget_group": "WANTS", "icon": "circle-ellipsis", "color": "#64748b"},
]

def init_db(db: Session = None):
    close_after = False
    if db is None:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        close_after = True

    try:
        # Check if already seeded
        existing_org = db.query(Organization).filter(Organization.slug == "acme-corp").first()
        if existing_org:
            return existing_org.id

        # 1. Create Organization
        org = Organization(
            name="Acme Financial Corp",
            slug="acme-corp",
            currency="USD",
            is_active=True
        )
        db.add(org)
        db.flush()

        # 2. Seed Default Categories
        cat_map = {}
        for c_data in DEFAULT_CATEGORIES:
            cat = Category(
                organization_id=org.id,
                name=c_data["name"],
                budget_group=c_data["budget_group"],
                icon=c_data["icon"],
                color=c_data["color"],
                is_system=True
            )
            db.add(cat)
            db.flush()
            cat_map[c_data["name"]] = cat.id

        # 3. Seed Users
        users_info = [
            ("admin@finflow.ai", "Admin123!@#", "Alexander Wright", RoleEnum.ORG_ADMIN, True),
            ("manager@finflow.ai", "Manager123!@#", "Sarah Jenkins", RoleEnum.FINANCE_MANAGER, False),
            ("analyst@finflow.ai", "Analyst123!@#", "David Chen", RoleEnum.FINANCIAL_ANALYST, False),
            ("auditor@finflow.ai", "Auditor123!@#", "Elena Rostova", RoleEnum.AUDITOR, False),
        ]

        created_users = {}
        for email, pwd, name, role, is_super in users_info:
            totp_sec = TOTPManager.generate_secret()
            rec_codes = TOTPManager.generate_recovery_codes()
            u = User(
                email=email,
                hashed_password=get_password_hash(pwd),
                full_name=name,
                is_active=True,
                is_superuser=is_super,
                totp_secret=totp_sec,
                is_totp_enabled=False,
                recovery_codes=json.dumps(rec_codes)
            )
            db.add(u)
            db.flush()
            created_users[email] = u

            member = OrganizationMember(
                organization_id=org.id,
                user_id=u.id,
                role=role
            )
            db.add(member)

        admin_user = created_users["admin@finflow.ai"]

        # 4. Seed Realistic Transactions across previous months and current month
        now = datetime.now(timezone.utc)
        demo_txs = [
            ("AWS Cloud Infrastructure", Decimal("1240.50"), "Business Expenses", "SUCCESS", 12.5, "LOW", now - timedelta(days=2)),
            ("Slack Enterprise Grid", Decimal("450.00"), "Business Expenses", "SUCCESS", 8.0, "LOW", now - timedelta(days=4)),
            ("WeWork Executive Office Suite", Decimal("3200.00"), "Rent", "SUCCESS", 5.0, "LOW", now - timedelta(days=10)),
            ("Stripe Settlement Payout", Decimal("-18500.00"), "Salary", "SUCCESS", 1.0, "LOW", now - timedelta(days=5)),
            ("Client Wire Transfer - Vertex Tech", Decimal("-12000.00"), "Investments", "SUCCESS", 2.0, "LOW", now - timedelta(days=12)),
            ("Whole Foods Executive Catering", Decimal("385.40"), "Food and Dining", "SUCCESS", 15.0, "LOW", now - timedelta(days=3)),
            ("Delta Airlines - Global FinTech Summit", Decimal("1420.00"), "Travel", "SUCCESS", 22.0, "LOW", now - timedelta(days=7)),
            ("Uber Technologies", Decimal("48.50"), "Transportation", "SUCCESS", 10.0, "LOW", now - timedelta(days=1)),
            ("Apple Store - MacBook Pro Fleet", Decimal("8999.00"), "Shopping", "PENDING_APPROVAL", 68.0, "MEDIUM", now - timedelta(hours=5)),
            ("Unusual Foreign Wire - Unknown Merchant", Decimal("14500.00"), "Other", "FLAGGED", 92.0, "CRITICAL", now - timedelta(hours=1)),
            ("Github Enterprise Subscription", Decimal("210.00"), "Business Expenses", "SUCCESS", 4.0, "LOW", now - timedelta(days=15)),
            ("Google Workspace Business", Decimal("180.00"), "Utilities", "SUCCESS", 6.0, "LOW", now - timedelta(days=18)),
            ("Chevron Fleet Fueling", Decimal("125.60"), "Transportation", "SUCCESS", 14.0, "LOW", now - timedelta(days=6)),
            ("Healthcare Premiums - BlueCross", Decimal("2400.00"), "Healthcare", "SUCCESS", 5.0, "LOW", now - timedelta(days=20)),
            ("MetLife Business Liability Policy", Decimal("850.00"), "Insurance", "SUCCESS", 3.0, "LOW", now - timedelta(days=22)),
        ]

        for idx, (m_name, amt, cat_name, status, r_score, r_level, tx_date) in enumerate(demo_txs):
            tx = Transaction(
                organization_id=org.id,
                user_id=admin_user.id,
                reference_id=f"TXN-{now.strftime('%Y%m%d')}-{1000 + idx}",
                idempotency_key=f"idemp-{1000 + idx}",
                amount=amt,
                currency="USD",
                merchant_name=m_name,
                description=f"Automated settlement: {m_name}",
                category_id=cat_map.get(cat_name, cat_map["Other"]),
                status=status,
                risk_score=r_score,
                risk_level=r_level,
                payment_method="CORPORATE_CARD" if amt > 0 else "DIRECT_DEPOSIT",
                created_at=tx_date,
                updated_at=tx_date
            )
            db.add(tx)
            db.flush()

            # Add lifecycle event
            evt = TransactionEvent(
                transaction_id=tx.id,
                from_status="INITIATED",
                to_status=status,
                reason="System automated processing lifecycle",
                created_at=tx_date
            )
            db.add(evt)

            # If FLAGGED or HIGH RISK, create a FraudCase with signals
            if status == "FLAGGED" or r_score > 60:
                fc = FraudCase(
                    organization_id=org.id,
                    transaction_id=tx.id,
                    risk_score=r_score,
                    risk_level=r_level,
                    recommendation="STEP_UP_AUTH" if r_score < 80 else "MANUAL_REVIEW",
                    status="OPEN",
                    investigator_notes="Triggered statistical anomaly and rapid velocity rules.",
                    created_at=tx_date
                )
                db.add(fc)
                db.flush()

                sig1 = FraudSignal(
                    fraud_case_id=fc.id,
                    rule_code="RUL-AMT-001",
                    signal_name="Sudden Outlier Amount Spike",
                    description=f"Transaction amount (${abs(amt)}) is 4.8 standard deviations above historical 30-day mean ($320.00).",
                    severity="HIGH",
                    weight=0.85
                )
                sig2 = FraudSignal(
                    fraud_case_id=fc.id,
                    rule_code="RUL-DEV-004",
                    signal_name="Unrecognized Device Fingerprint",
                    description="Session originated from an unrecognized user-agent and untrusted ASN subnet.",
                    severity="CRITICAL" if r_score > 80 else "MEDIUM",
                    weight=0.90
                )
                db.add_all([sig1, sig2])

        # 5. Seed Subscriptions
        subs = [
            ("AWS Cloud Services", Decimal("1240.50"), "MONTHLY", now + timedelta(days=12), "Business Expenses"),
            ("Slack Enterprise Grid", Decimal("450.00"), "MONTHLY", now + timedelta(days=8), "Business Expenses"),
            ("Google Workspace", Decimal("180.00"), "MONTHLY", now + timedelta(days=14), "Utilities"),
            ("Github Enterprise", Decimal("210.00"), "MONTHLY", now + timedelta(days=18), "Business Expenses"),
            ("Zoom Video Communications", Decimal("85.00"), "MONTHLY", now + timedelta(days=5), "Business Expenses"),
            ("Bloomberg Professional Terminal", Decimal("2200.00"), "MONTHLY", now + timedelta(days=25), "Business Expenses"),
        ]
        for m_name, amt, cycle, renew_dt, cat_name in subs:
            sub = Subscription(
                organization_id=org.id,
                user_id=admin_user.id,
                merchant_name=m_name,
                amount=amt,
                currency="USD",
                billing_cycle=cycle,
                next_renewal_date=renew_dt,
                category_id=cat_map.get(cat_name),
                status="ACTIVE",
                is_auto_detected=True
            )
            db.add(sub)

        # 6. Seed Current Month Budget (50/30/20)
        curr_month = now.strftime("%Y-%m")
        budget = Budget(
            organization_id=org.id,
            user_id=admin_user.id,
            month=curr_month,
            total_income=Decimal("30500.00"),
            total_allocated=Decimal("24500.00"),
            needs_target_pct=Decimal("50.00"),
            wants_target_pct=Decimal("30.00"),
            savings_target_pct=Decimal("20.00"),
            strategy="STANDARD_50_30_20",
            is_active=True
        )
        db.add(budget)
        db.flush()

        budget_allocations = [
            ("Rent", Decimal("3500.00")),
            ("Business Expenses", Decimal("5000.00")),
            ("Utilities", Decimal("800.00")),
            ("Healthcare", Decimal("2500.00")),
            ("Insurance", Decimal("1000.00")),
            ("Transportation", Decimal("700.00")),
            ("Food and Dining", Decimal("2000.00")),
            ("Shopping", Decimal("2500.00")),
            ("Entertainment", Decimal("1000.00")),
            ("Travel", Decimal("1500.00")),
            ("Savings", Decimal("4000.00")),
        ]
        for c_name, alloc in budget_allocations:
            bc = BudgetCategory(
                budget_id=budget.id,
                category_id=cat_map[c_name],
                allocated_amount=alloc
            )
            db.add(bc)

        # 7. Seed Financial Goals
        g1 = FinancialGoal(
            organization_id=org.id,
            user_id=admin_user.id,
            title="Q4 Operating Reserve Buffer",
            target_amount=Decimal("50000.00"),
            current_amount=Decimal("38500.00"),
            currency="USD",
            target_date=now + timedelta(days=90),
            category="EMERGENCY_FUND",
            status="IN_PROGRESS"
        )
        g2 = FinancialGoal(
            organization_id=org.id,
            user_id=admin_user.id,
            title="Enterprise Cloud Infrastructure Migration",
            target_amount=Decimal("25000.00"),
            current_amount=Decimal("17200.00"),
            currency="USD",
            target_date=now + timedelta(days=45),
            category="ASSET",
            status="IN_PROGRESS"
        )
        db.add_all([g1, g2])

        # 8. Seed Receipts
        rec = Receipt(
            organization_id=org.id,
            user_id=admin_user.id,
            file_name="Apple_Store_Invoice_8999.pdf",
            file_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            merchant_name="Apple Store Retail",
            total_amount=Decimal("8999.00"),
            currency="USD",
            tax_amount=Decimal("720.00"),
            invoice_number="INV-APP-2026-9921",
            receipt_date=now - timedelta(hours=5),
            category_id=cat_map["Shopping"],
            status="VERIFIED",
            raw_text="Apple Retail Store #412\nInvoice: INV-APP-2026-9921\n3x MacBook Pro 16-inch M3 Max - $8,999.00\nTax: $720.00\nTotal: $8,999.00"
        )
        db.add(rec)
        db.flush()

        line1 = ReceiptLineItem(
            receipt_id=rec.id,
            description="MacBook Pro 16-inch M3 Max 64GB 1TB",
            quantity=3,
            unit_price=Decimal("2999.66"),
            total_price=Decimal("8999.00")
        )
        db.add(line1)

        # 9. Seed Audit Logs
        audit = AuditLog(
            organization_id=org.id,
            actor_id=admin_user.id,
            actor_email=admin_user.email,
            action="ORGANIZATION_INITIALIZED",
            resource_type="ORGANIZATION",
            resource_id=org.id,
            ip_address="127.0.0.1",
            request_id="REQ-INIT-001",
            metadata_json=json.dumps({"seeded_categories": len(cat_map), "status": "READY"})
        )
        db.add(audit)

        # 10. Seed Notifications
        n1 = Notification(
            organization_id=org.id,
            user_id=admin_user.id,
            type="FRAUD_ALERT",
            title="High-Risk Transaction Flagged",
            message="Transaction of $14,500.00 with Unknown Merchant was flagged with Risk Score 92/100.",
            data_json=json.dumps({"risk_score": 92, "recommendation": "MANUAL_REVIEW"}),
            is_read=False
        )
        n2 = Notification(
            organization_id=org.id,
            user_id=admin_user.id,
            type="BUDGET_EXCEEDED",
            title="Shopping Budget Warning",
            message="Shopping category has reached 88% of monthly allocation ($2,200 / $2,500).",
            data_json=json.dumps({"category": "Shopping", "pct": 88}),
            is_read=False
        )
        db.add_all([n1, n2])

        db.commit()
        return org.id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        if close_after:
            db.close()

if __name__ == "__main__":
    org_id = init_db()
    print(f"Database successfully initialized with Org ID: {org_id}")
