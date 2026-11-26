FROM python:3.12-slim
WORKDIR /app
ENV PYTHONPATH=/app/backend/shared:/app/services/api-gateway/app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
COPY backend /app/backend
COPY services/api-gateway /app/services/api-gateway
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "/app/services/api-gateway/app"]

