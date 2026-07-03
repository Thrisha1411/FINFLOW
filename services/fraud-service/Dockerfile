FROM python:3.12-slim
WORKDIR /app
ENV PYTHONPATH=/app/backend/shared:/app/services/fraud-service/app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
COPY backend /app/backend
COPY services/fraud-service /app/services/fraud-service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "/app/services/fraud-service/app"]

