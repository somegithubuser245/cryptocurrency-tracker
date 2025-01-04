# Crypto Price Tracker

A real-time cryptocurrency price visualization platform that displays OHLC (Open, High, Low, Close) data from Binance API. Built with FastAPI, React, and Redis caching.

## Features
- Real-time cryptocurrency OHLC data visualization
- Interactive candlestick charts using Lightweight Charts
- Multiple time intervals (5m, 30m, 1h, 4h, 1d, 1w, 1M)
- Support for major cryptocurrencies (BTC, ETH, SOL, ADA, AVAX, DOT)
- Data caching with Redis for improved performance

## Tech Stack

### Backend
- Python with FastAPI
- Redis for caching
- Binance API integration
- Uvicorn ASGI server

### Frontend
- React with TypeScript
- TailwindCSS for styling
- Lightweight Charts for candlestick visualization

### DevOps
- Docker & Docker Compose
- Testing with pytest

## Getting Started

### Prerequisites
- Docker and Docker Compose
- For local development:
  - Node.js
  - Python 3.11+
  - Redis

### System Requirements
- RAM: ~200MB for Docker containers
- No API keys required
- Default ports used:
  - Frontend: 5173 (Vite)
  - Backend: 8000 (Uvicorn)
  - Redis: 6379

### Docker Setup
1. Clone the repository
```bash
git clone <repository-url>
cd cryptocurrency-tracker
```

2. Start the application
```bash
docker-compose up
```

The application will be available at http://localhost:5173

You should see logs from both frontend and backend containers at startup.

### Local Development Setup

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Redis Setup (Windows/WSL)

1. Install Redis
```bash
# Add Redis repository
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg

# Add Redis repository to sources
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

# Update package list
sudo apt-get update

# Install Redis
sudo apt-get install redis
```

2. Start Redis server
```bash
sudo service redis-server start
```

3. (Optional) Access Redis CLI
```bash
redis-cli
```
You can test the connection with `KEYS *` to view cached keys.

## Customization

The application can be customized without major code changes:

### Adding Cryptocurrency Pairs
1. Check available pairs on [Binance](https://binance.com)
2. Add new pairs to `SUPPORTED_PAIRS` in `app/config/binance_config.py`
3. Frontend will automatically display new pairs on refresh

### Adding Time Intervals
1. Check available intervals in [Binance API Documentation](https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints)
2. Add new intervals to `TIME_RANGES` in `app/config/binance_config.py`
3. Add corresponding cache TTL in `CACHE_TTL_CONFIG`

## API Endpoints

- `GET /api/crypto/config/pairs` - Get supported cryptocurrency pairs
- `GET /api/crypto/config/timeranges` - Get available time intervals
- `GET /api/crypto/{crypto_id}/{data_type}?interval={interval}` - Get OHLC data

Full API documentation is available at http://localhost:8000/docs when the backend is running.

## Project Structure
```
├── backend/
│   ├── app/
│   │   ├── config/
│   │   │   ├── binance_config.py
│   │   │   └── config.py
│   │   ├── models/
│   │   │   └── schemas.py
│   │   └── services/
│   │       ├── api_call_manager.py
│   │       ├── binance.py
│   │       └── caching.py
│   └── tests/
└── frontend/
    ├── src/
    │   ├── components/
    │   │   └── CryptoChart.tsx
    │   └── services/
    └── public/
```

## Testing

Run the backend tests:
```bash
cd backend
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request