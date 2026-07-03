#!/usr/bin/env sh
set -eu
docker compose pull
docker compose up -d --build
docker compose run --rm auth-service alembic upgrade head

