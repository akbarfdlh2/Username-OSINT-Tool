# Container untuk web.py (FastAPI). Cocok untuk Hugging Face Spaces, Railway, Fly.io, dll.
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Host menyuntik PORT lewat environment (HF Spaces = 7860).
ENV PORT=7860
EXPOSE 7860

CMD ["sh", "-c", "uvicorn web:app --host 0.0.0.0 --port ${PORT}"]
