# FinFlow AI Architecture

FinFlow AI uses microservices behind an API gateway. Services are isolated by bounded context but share foundational libraries for logging, configuration, security, database connectivity, schemas, events, and core domain primitives.

## Event Flow

```mermaid
sequenceDiagram
  participant UI as React Dashboard
  participant GW as API Gateway
  participant PAY as Payment Service
  participant FRAUD as Fraud Service
  participant KAFKA as Kafka
  participant AUDIT as Audit Service
  participant NOTIF as Notification Service

  UI->>GW: Create transaction
  GW->>PAY: POST /transactions
  PAY->>FRAUD: Risk scoring through shared engine/API
  PAY->>KAFKA: Transaction Created / Flagged
  KAFKA->>AUDIT: Persist workflow history
  KAFKA->>NOTIF: Alert finance operators
  GW-->>UI: Workflow status
```

## Database ER Diagram

```mermaid
erDiagram
  USERS ||--o{ USER_ROLES : has
  ROLES ||--o{ USER_ROLES : grants
  ROLES ||--o{ ROLE_PERMISSIONS : contains
  PERMISSIONS ||--o{ ROLE_PERMISSIONS : allows
  USERS ||--o{ DEVICES : uses
  USERS ||--o{ SESSIONS : owns
  TRANSACTIONS ||--o{ TRANSACTION_EVENTS : records
  TRANSACTIONS ||--o{ FRAUD_CASES : triggers
  BUDGETS ||--o{ BUDGET_ALERTS : emits
  USERS {
    uuid id
    string email
    string organization_id
    boolean is_active
  }
  TRANSACTIONS {
    uuid id
    string organization_id
    numeric amount
    string status
    numeric risk_score
  }
  FRAUD_CASES {
    uuid id
    numeric risk_score
    string status
  }
  AUDIT_LOGS {
    uuid id
    string action
    string resource_type
  }
```

## Operational Model

- PostgreSQL is the source of truth.
- Redis powers Celery queues and cache-ready workflows.
- Kafka carries durable domain events.
- Prometheus scrapes service metrics.
- Grafana provisions an overview dashboard.
- NGINX handles edge routing for frontend, API, and WebSocket traffic.

