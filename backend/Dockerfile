FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt ./
RUN apt-get update \
    && apt-get -y install libpq-dev gcc
RUN pip install -r requirements.txt

# Copy application code
COPY src/ ./

EXPOSE 8000

CMD ["uvicorn", "routes.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]