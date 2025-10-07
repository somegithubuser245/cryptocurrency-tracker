FROM python:3.13-slim

WORKDIR /app

# libpq is a postgres dev library, needed for psycopg2
# psycopg2 needs gcc as well, for compilation
RUN apt-get update \
    && apt-get -y install libpq-dev gcc
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy application code
COPY src/ ./

EXPOSE 8000

CMD ["uvicorn", "routes.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]