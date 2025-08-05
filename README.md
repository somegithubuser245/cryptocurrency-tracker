# Cryptocurrency Historical Price Analyzer

A cryptocurrency analysis tool to fetch, compare, and visualize historical OHLC (Open, High, Low, Close) price data for trading pairs across multiple exchanges. This application provides a REST API backend built with FastAPI and a React-based frontend for data visualization.

This repository is tagged at `v0.1.0` to represent this initial version. Future development will focus on real-time analysis and automated trading strategies on a separate branch.

## Core Features (v0.1.0)

- **Multi-Exchange Data Aggregation**: Fetches historical OHLC data from exchanges using the CCXT library (Currently: Binance, OKX, Bybit, MEXC, BingX, Gate.io, and KuCoin).
- **Pair Price Comparison**: Compares the historical prices of a single trading pair across multiple exchanges to identify potential spread opportunities.
- **Max Spread Calculation**: Analyzes historical data to find the maximum price spread between exchanges for a given pair.
- **Interactive Data Visualization**: The frontend provides charts to visually compare OHLC data from different sources simultaneously.
- **Dynamic Pair Discovery**: Automatically finds all tradable pairs supported by the integrated exchanges.
- **Cached Responses**: Utilizes Redis to cache API responses for improved performance.

<img width="1014" height="816" alt="image_2025-08-05_23-31-45" src="https://github.com/user-attachments/assets/b77c7f7b-3157-4ea3-be26-3527dd3e9e8b" />


## Tech Stack

### Backend

- **FastAPI**: High-performance asynchronous web framework for the REST API.
- **CCXT**: Unified library for cryptocurrency exchange API interaction.
- **Redis**: In-memory data store used for caching.
- **Pandas**: Data manipulation and analysis of OHLC data.
- **Uvicorn**: Lightning-fast ASGI server.

### Frontend

- **React with TypeScript**: Modern component-based UI.
- **TailwindCSS**: Utility-first styling framework.
- **Lightweight Charts**: Professional financial data visualization.

### DevOps & Infrastructure

- **Docker & Docker Compose**: Containerized deployment for easy setup.

## Architecture

The system is a classic client-server application:

1.  **Frontend (React)**: A user-facing dashboard that allows users to select a trading pair and see it visualized across multiple exchanges.
2.  **Backend (FastAPI)**: Exposes a REST API that the frontend consumes. When a request is received, it fetches the necessary historical data from the specified exchanges via the CCXT library, performs the price comparison and spread calculations, and returns the data.
3.  **Cache (Redis)**: Before making external API calls, the backend checks Redis for cached data to reduce latency and avoid hitting exchange rate limits.

## Getting Started

### Prerequisites

- Docker and Docker Compose
- For local development:
  - Node.js (v18+)
  - Python 3.11+
  - Redis

### Quick Start with Docker

1. Clone the repository:

   ```bash
   git clone https://github.com/somegithubuser245/cryptocurrency-tracker.git
   cd cryptocurrency-tracker
   ```

2. (Optional) To use this specific version, checkout the tag:

   ```bash
   git checkout v0.1.0
   ```

3. Start all services:
   ```bash
   docker-compose up --build
   ```


4. Access the application

- **Frontend**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs
- **Redis Insight**: redis-cli

### Local Development Setup

#### Backend Development

```bash
cd backend
pip install -r requirements.txt

# Start Redis (if not using Docker)
redis-server

# Start the FastAPI server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Development

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


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
