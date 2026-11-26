# API Guide

All services expose `/health`, `/metrics`, and `/docs`.

Gateway route shape:

| Capability | Gateway Path | Upstream |
| --- | --- | --- |
| Auth | `/auth/*` | auth-service |
| Transactions | `/transactions/*` | payment-service |
| Fraud | `/fraud/*` | fraud-service |
| Analytics | `/analytics/*` | analytics-service |
| AI Assistant | `/assistant/*` | ai-assistant-service |
| Subscriptions | `/subscriptions/*` | subscription-service |
| Notifications | `/notifications/*` | notification-service |
| Audit | `/audit/*` | audit-service |

## Example

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "content-type: application/json" \
  -d '{"email":"ops@example.com","password":"ChangeMe12345!","full_name":"Ops Lead","organization_id":"acme"}'
```

```bash
curl -X POST http://localhost:8000/transactions \
  -H "authorization: Bearer <token>" \
  -H "content-type: application/json" \
  -d '{"merchant":"AWS India","amount":153000,"currency":"INR"}'
```
