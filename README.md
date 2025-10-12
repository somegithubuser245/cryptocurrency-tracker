# Cryptocurrency Tracker

A full-stack tool for analyzing historical cryptocurrency spreads. The backend (FastAPI + Celery) ingests OHLCV data from multiple exchanges via CCXT, stores normalized results in Postgres, and makes them available through REST endpoints. The frontend (React + Vite) visualizes batch progress and computed spreads in real time.

## Project Structure

- **Backend** – FastAPI service with Celery workers, Redis cache, and Postgres migrations.
- **Frontend** – React dashboard with auto-refreshing computed spread table.

Key modules:
- [`background.batch_fetch_ohlc`](backend/src/background/batch_fetch_ohlc.py) – Orchestrates pair discovery, OHLC downloads, and Celery compute jobs.
- [`background.celery.celery_spreads.py`](backend/src/background/celery/celery_spreads.py) - Celery workers setup
- [`background.db.user_api`](backend/src/background/db/user_api.py) – Aggregates batch status and computed spreads.
- Frontend React app bootstrapped in [`src/main.tsx`](frontend/src/main.tsx) and [`src/App.tsx`](frontend/src/App.tsx).

## Features

- Batch initialization and fetching of supported trading pairs across configured exchanges.
- Parellel spread computation with celery.
- REST endpoints to trigger workflows and read progress/spread summaries.
- React dashboard showing batch processing stats and live-updating spread table.

## Getting Started

### Prerequisites

- Docker & Docker Compose (recommended)  
  or
- Python 3.13, Node.js 20+, Redis, Postgres (for manual setup)

### Quick Start (Docker)

```sh
docker-compose up --build
```

Services exposed:

- Backend API: http://localhost:8000
- Frontend UI: http://localhost:5173
- Redis: localhost:6379
- Postgres: localhost:5432
- Flower (Celery monitor): http://localhost:5555
- Adminer (DB UI): http://localhost:8080

### Manual Setup

1. **Backend**

   ```sh
   cd backend
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn routes.main:app --reload
   ```

2. **Celery Worker**

   ```sh
   cd backend
   celery -A background.celery.celery_conf worker --loglevel=INFO
   ```

3. **Frontend**

   ```sh
   cd frontend
   npm install
   npm run dev
   ```

Ensure Redis and Postgres are running and accessible (configure via environment variables if needed).

## Usage

1. Open the frontend dashboard.
2. Click **“Start Spread Computation”** to initialize pairs and launch batch processing.
3. Monitor batch stats and computed spreads on the dashboard; results auto-refresh.

## Configuration

- Batch settings, Timezone, Supported Exchanges: [`backend/src/config/config.py`](backend/src/config/config.py)
- Database related Config: [`backend/src/config/database.py`](backend/src/config/database.py)
- Docker services: [`docker-compose.yml`](docker-compose.yml)

## License

MIT – see [LICENSE](LICENSE).