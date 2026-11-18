# 1. Base Python image
FROM python:3.11-slim

# 2. Working directory
WORKDIR /app

# 3. Python environment settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 4. Install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copy application code
COPY app/ ./app/

# 6. Create storage directories
RUN mkdir -p storage/uploads storage/vector_db

# 7. Create a non-root user
RUN groupadd --system appgroup && \
    useradd --system --gid appgroup --create-home appuser && \
    chown -R appuser:appgroup /app/storage

# 8. Switch to non-root user
USER appuser

# 9. Expose FastAPI port
EXPOSE 8000

# 10. Start FastAPI
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]