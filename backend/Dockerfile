FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy application code
COPY . ./

EXPOSE 8000

# Test imports first, then start server
CMD ["sh", "-c", "python test_imports.py && python -m uvicorn src.routes.main:app --host 0.0.0.0 --port 8000 --reload"]