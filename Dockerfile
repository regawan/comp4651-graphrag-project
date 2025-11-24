FROM python:3.11-slim

# 1. Basic setup
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# 2. Install system and python dependencies
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy the app code
COPY . .

# 4. Expose port for rest api (FastAPI)
EXPOSE 8000

# 5. Run app (--workers 4 for simple uvicorn load balancing)
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
