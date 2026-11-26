# Deployment Guide

## Environments

- Development: Docker Compose on one host.
- Staging: same topology with managed Postgres, Redis, Kafka.
- Production: container orchestrator, TLS ingress, secret manager, managed observability.

## Required Secrets

- `JWT_SECRET`
- `DATABASE_URL`
- `REDIS_URL`
- `KAFKA_BOOTSTRAP_SERVERS`
- `OPENAI_API_KEY`
- SMTP credentials

## Release

```bash
./scripts/deploy.sh
```

## Production Hardening

- Enforce TLS and HSTS at ingress.
- Rotate JWT secrets using key IDs.
- Enable database backups and PITR.
- Configure Kafka retention by topic.
- Add dead-letter topics for failed background jobs.
- Replace demo notification delivery with an enterprise email/SMS provider.

