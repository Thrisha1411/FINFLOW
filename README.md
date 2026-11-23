# FinFlow AI
### Enterprise Financial Operations, Fraud Intelligence & Payment Automation Platform

FinFlow AI is an AI-native financial operations SaaS platform engineered for enterprises, financial institutions, and high-growth organizations. It unifies high-throughput payment lifecycle orchestration, hybrid AI fraud surveillance (Isolation Forest + behavioral rule engines), automated OCR receipt and invoice processing, deterministic 50/30/20 budgeting, predictive cash-flow forecasting, recurring subscription tracking, and an explainable financial assistant grounded in real database records.

---

## Key Differentiators & Product Principles

- **Zero Hardcoded Numbers**: Every dashboard metric, forecast, and chart is computed dynamically from persistent relational records.
- **Zero Hallucinated Financial Figures**: The AI Financial Assistant calculates deterministic figures through SQL queries and utilizes LLMs exclusively for synthesis, summaries, and evidence-based explanations.
- **Hybrid AI Fraud Intelligence**: Combines statistical anomaly detection (`Isolation Forest` tree scoring) with deterministic heuristic surveillance (velocity bursts, outlier amounts, device trust).
- **Strict Multi-Tenant Isolation**: Enforced at the database and API authorization layer using Granular Role-Based Access Control (`SUPER_ADMIN`, `ORG_ADMIN`, `FINANCE_MANAGER`, `FINANCIAL_ANALYST`, `AUDITOR`, `CUSTOMER`).
- **Complete Payment Orchestration Simulation**: Explicit state machine modeling (`INITIATED` → `VALIDATING` → `RISK_ANALYSIS` → `PENDING_APPROVAL` → `PROCESSING` → `SUCCESS` / `FLAGGED` → `AUDIT_RECORDED`) with provider adapter compatibility for Stripe and Razorpay.

---

## Technology Stack

- **Backend**: Python 3.13, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, PostgreSQL, SQLite (testing).
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons, Recharts, React Router, Axios.
- **AI / ML**: Scikit-Learn Isolation Forest, Exponential Smoothing (Holt linear trend), OCR Parsing with PyMuPDF, Rule Engine.
- **Authentication**: OAuth2 JWT, Refresh Token Rotation, RFC 6238 TOTP Two-Factor Authentication, Cryptographic Recovery Codes.
- **Infrastructure & Distributed Systems**: Docker Compose, NGINX API Gateway, Redis Pub/Sub, Apache Kafka event schemas, Prometheus, Grafana.

---

## Quick Start (Local Development)

### 1. Prerequisites
- Python 3.11+
- Node.js 20+ and `pnpm`
- Git

### 2. Backend Setup
```bash
# Clone the repository
git clone https://github.com/organization/finflow.git
cd FinFlow

# Create virtual environment and install dependencies
python -m pip install -r backend/requirements.txt

# Initialize database schema and seed realistic financial demo data
python -m backend.app.db.init_db

# Run backend development server
uvicorn backend.app.main:app --reload --port 8000
```
Backend API will be live at `http://localhost:8000` (Swagger docs: `http://localhost:8000/api/v1/docs`).

### 3. Frontend Setup
```bash
cd frontend
pnpm install
pnpm dev
```
Frontend application will be accessible at `http://localhost:5173`.

---

## Quick Start (Docker Deployment)

Deploy the entire production stack (NGINX Gateway, Frontend, FastAPI Backend, PostgreSQL 16, Redis 7, Kafka, Zookeeper, Prometheus, Grafana) with a single command:

```bash
docker compose up --build -d
```

- **Web Dashboard**: `http://localhost`
- **REST API**: `http://localhost/api/v1`
- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3000` (admin/admin)

---

## Demo Personas & Pre-seeded Accounts

| Role | Email | Password | Scope & Permissions |
| :--- | :--- | :--- | :--- |
| **Super / Org Admin** | `admin@finflow.ai` | `Admin123!@#` | Full system access, user management, 2FA setup, settings. |
| **Finance Manager** | `manager@finflow.ai` | `Manager123!@#` | Transaction approvals, refund execution, budget planning. |
| **Financial Analyst**| `analyst@finflow.ai` | `Analyst123!@#` | Fraud investigation, root cause variance, forecasting analysis. |
| **Auditor** | `auditor@finflow.ai` | `Auditor123!@#` | Read-only compliance access, audit trail ledger inspection. |

---

## Automated Test Suite

Run the full end-to-end backend test suite:
```bash
python -m pytest backend/tests/test_api.py -v
```

Build and typecheck the frontend:
```bash
cd frontend
pnpm run build
```

---

## Architectural Documentation
- [System Architecture & State Machines](docs/ARCHITECTURE.md)
- [REST API Reference & Endpoints](docs/API_REFERENCE.md)
- [Postman Collection](docs/POSTMAN_COLLECTION.json)
