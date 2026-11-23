# FinFlow AI REST API Reference

Base URL: `http://localhost:8000/api/v1`

All authenticated endpoints require an `Authorization: Bearer <JWT_ACCESS_TOKEN>` header.

---

## 1. Authentication & Identity
- `POST /auth/register`: Register new user and organization.
- `POST /auth/login`: Authenticate with email, password, and optional TOTP 2FA code.
- `GET /auth/me`: Retrieve authenticated user context and organization role.
- `POST /auth/2fa/setup`: Generate RFC 6238 TOTP base32 secret and provisioning URI.
- `POST /auth/2fa/enable`: Verify 6-digit TOTP token and enable two-factor authentication.

## 2. Dashboard Telemetry
- `GET /dashboard/overview`: Real-time aggregated financial KPI metrics, savings rate, health score, and recent transactions.

## 3. Payments & Transactions
- `GET /transactions`: List transactions with search, status filter, and pagination.
- `POST /transactions`: Initiate transaction through AI fraud scoring and payment lifecycle orchestration.
- `GET /transactions/{id}`: Retrieve transaction details and lifecycle event history.
- `POST /transactions/{id}/approve`: Manually approve a pending/flagged transaction.
- `POST /transactions/{id}/refund`: Process full or partial refund.

## 4. AI Fraud Intelligence
- `GET /fraud/cases`: List active and resolved fraud cases.
- `GET /fraud/cases/{id}`: Detailed fraud case with triggered explainable signals.
- `PATCH /fraud/cases/{id}`: Resolve fraud case (`RESOLVED_BENIGN` or `CONFIRMED_FRAUD`).

## 5. Receipt & Invoice Scanner
- `POST /receipts/upload`: Upload receipt document (PDF, PNG, JPG), compute SHA-256 duplicate hash, and execute OCR.
- `GET /receipts`: List uploaded documents.
- `POST /receipts/confirm`: Verify extracted fields and convert into settled transaction.

## 6. Smart Budgeting & Forecasting
- `GET /budgets/50-30-20`: Retrieve actual 50/30/20 category allocations and recommendations.
- `GET /budgets/health-score`: Retrieve 5-pillar transparent budget health score.
- `GET /budgets/next-month-plan`: Generate next-month budget recommendations.

## 7. Recurring Subscriptions
- `GET /subscriptions`: List active subscriptions and upcoming renewals.
- `POST /subscriptions`: Register a subscription.
- `GET /subscriptions/analytics`: Monthly recurring spend, annual projection, and renewals within 30 days.
- `GET /subscriptions/detected`: Auto-detected recurring transaction cadences.

## 8. AI Financial Assistant & What-If Simulator
- `POST /assistant/chat`: Natural language assistant grounded in verified database queries.
- `POST /simulator/simulate`: What-If financial scenario simulator.
- `GET /root-cause/analyze`: AI period-over-period variance root cause analysis.

## 9. Compliance & Audit
- `GET /audit`: Query immutable append-only audit trail logs.
- `GET /notifications`: In-app notification cards.
- `PATCH /notifications/{id}/read`: Mark notification as read.
