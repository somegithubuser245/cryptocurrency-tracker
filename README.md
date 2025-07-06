# Cryptocurrency Arbitrage Tracker

A real-time cryptocurrency arbitrage tracking platform that identifies and monitors price spreads across multiple exchanges. Built with FastAPI, React, CCXT, and Redis caching for high-performance cross-exchange analysis.

## Features

- **Cross-Exchange Arbitrage Detection**: Monitor price spreads across 7+ cryptocurrency exchanges
- **Real-Time Spread Analysis**: Live tracking of current price differences between exchange pairs
- **Historical Max Spread Calculation**: 4-hour maximum spread tracking for better opportunity identification (in progress)
- **Interactive Data Visualization**: Compare OHLC data across multiple exchanges simultaneously
- **Multi-Exchange Support**: Binance, OKX, Bybit, MEXC, BingX, Gate.io, and KuCoin integration
- **Comprehensive Pair Coverage**: Automatic discovery of supported trading pairs across all exchanges

## Tech Stack

### Backend

- **FastAPI**: High-performance async web framework
- **CCXT**: Unified cryptocurrency exchange API integration
- **Redis**: Advanced caching and data management
- **Pandas**: Large-scale financial data processing and analysis
- **Uvicorn**: Lightning-fast ASGI server
- **Pytest**: Comprehensive testing framework

### Frontend

- **React with TypeScript**: Modern component-based UI
- **TailwindCSS**: Utility-first styling framework
- **Lightweight Charts**: Professional financial data visualization
- **WebSocket Integration**: Real-time data streaming

### DevOps & Infrastructure

- **Docker & Docker Compose**: Containerized deployment
- **Multi-stage builds**: Optimized container images
- **Environment configuration**: Flexible deployment options

## Architecture Overview

### Core Components

#### 1. Exchange Integration Layer

- **CCXT Wrapper**: Unified interface for multiple cryptocurrency exchanges
- **Async Processing**: High-performance concurrent API calls

#### 2. Spread Analysis Engine (in progress)

- **Real-Time Monitoring**: Live price difference tracking between exchange pairs
- **Historical Analysis**: 4-hour maximum spread calculation with configurable granularity
- **Pair Discovery**: Automatic identification of supported trading pairs per exchange
- **Opportunity Ranking**: Sort by potential arbitrage profitability

#### 3. Data Management (in progress)

- **Redis Caching**: Multi-level caching strategy for different data types
- **Pandas Integration**: Large-scale data processing and analysis
- **WebSocket Streaming**: Real-time data updates for current spreads
- **REST API**: Static data and configuration endpoints

### Supported Exchanges

- **Everything included in the ccxt docs**

## Getting Started

### Prerequisites

- Docker and Docker Compose
- For local development:
  - Node.js (v18+)
  - Python 3.11+
  - Redis

### System Requirements

- **RAM**: 500MB for Docker containers 
- **CPU**: Multi-core recommended for concurrent exchange API calls
- **Network**: Stable internet connection for real-time data
- **Storage**: Minimal (data is cached, not permanently stored)
- **API Keys**: None required for basic functionality
- **Default ports**:
  - Frontend: 5173 (Vite)
  - Backend: 8000 (Uvicorn)
  - Redis: 6379

### Quick Start with Docker

1. Clone the repository

```bash
git clone https://github.com/somegithubuser245/cryptocurrency-tracker.git
cd cryptocurrency-tracker
```

2. Start all services

```bash
docker-compose up --build
```

3. Access the application

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

## API Endpoints

### Static Data

- `GET /api/static/config/exchanges` - Get supported exchanges and their configurations
- `GET /api/static/config/pairs` - Get supported trading pairs across all exchanges
- `GET /api/static/config/timeframes` - Get available time intervals for historical data

### Real-Time Data

- `GET /api/crypto/{exchange}/{pair}/ohlc?interval={interval}` - Get OHLC data for specific exchange and pair
- `GET /api/spreads/current` - Get current spread data across all pairs and exchanges
- `GET /api/spreads/historical/{pair}?hours={hours}` - Get historical maximum spreads

### WebSocket Endpoints

- `WS /ws/spreads/live` - Real-time spread updates
- `WS /ws/prices/{exchange}/{pair}` - Live price updates for specific pair

### Configuration

- `GET /api/config/supported-pairs` - Get dynamically discovered trading pairs
- `GET /api/config/exchanges` - Get active exchange configurations

Full API documentation is available at http://localhost:8000/docs when the backend is running.

## Current Features & Roadmap

### ✅ Completed Features

- [x] Multi-exchange OHLC data fetching via CCXT
- [x] FastAPI backend with async processing
- [x] React frontend with TypeScript
- [x] Docker containerization
- [x] Basic exchange pair discovery
- [x] Chart comparison between exchanges

### 🚧 In Progress

- [ ] **Spread Analysis Table**: Main frontend table showing current and historical spreads
- [ ] **WebSocket Integration**: Real-time spread updates
- [ ] **Pair Discovery System**: Automatic detection of supported pairs per exchange
- [ ] **Historical Max Spread Calculation**: 4-hour maximum spread tracking
- [ ] **Pandas Integration**: Large-scale data processing optimization

### 🔄 Frontend Improvements (In Progress)

- [ ] **Visual Enhancements**:
  - [ ] Remove duplicate column headers
  - [ ] Implement sorting by 4-hour max spread
  - [ ] Add color coding for positive/negative spreads
  - [ ] Responsive table design
- [ ] **Data Management**:
  - [ ] State synchronization between REST API and WebSocket data
  - [ ] Efficient data fetching and caching strategies
  - [ ] Real-time spread calculations

### 🔮 Planned Features

- [ ] **Advanced Analytics**:

  - [ ] Trend analysis and spread prediction
  - [ ] Arbitrage opportunity alerts
  - [ ] Portfolio tracking integration
  - [ ] Risk assessment tools

- [ ] **Trading Integration**:

  - [ ] Partial fill management system
  - [ ] Position tracking and PnL calculation
  - [ ] Trade execution across multiple exchanges

- [ ] **Performance Optimizations**:
  - [ ] Database integration for historical data
  - [ ] Improved caching strategies
  - [ ] Rate limiting and request optimization

## Project Structure

```
├── backend/
│   ├── src/
│   │   ├── main.py                        # FastAPI application entry point
│   │   ├── config/
│   │   │   ├── config.py                  # Main configuration and exchange enums
│   │   │   └── binance_config.py         # Binance-specific configuration
│   │   ├── routes/
│   │   │   ├── main.py                    # Main API routes
│   │   │   ├── crypto_data.py             # OHLC data endpoints
│   │   │   ├── static_data.py             # Static configuration endpoints
│   │   │   ├── scan_spreads.py            # Spread analysis endpoints (WIP)
│   │   │   └── models/
│   │   │       └── schemas.py             # Pydantic models and data schemas
│   │   ├── services/
│   │   │   ├── external_api_caller.py     # CCXT wrapper and exchange integration
│   │   │   ├── api_call_manager.py        # API rate limiting and management
│   │   │   └── caching.py                 # Redis caching implementation
│   │   └── utils/
│   │       └── timeframes_equalizer.py    # Time interval normalization
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_api.py                    # API endpoint tests
│   ├── requirements.txt                   # Python dependencies
│   └── Dockerfile                         # Backend container configuration
├── frontend/
│   ├── src/
│   │   ├── main.tsx                       # React application entry point
│   │   ├── App.tsx                        # Main application component
│   │   ├── components/
│   │   ├── api/
│   │   ├── hooks/
│   │   ├── types/
│   │   │   └── index.ts                   # TypeScript type definitions
│   │   ├── utils/
│   │   │   └── priceFormatter.ts          # Price formatting utilities
│   │   └── assets/
│   ├── public/
│   ├── package.json                       # Frontend dependencies
│   ├── vite.config.ts                     # Vite build configuration
│   ├── tsconfig.json                      # TypeScript configuration
│   └── Dockerfile                         # Frontend container configuration
├── docker-compose.yml                     # Multi-container orchestration
├── pyproject.toml                         # Python project configuration
└── README.md                              # This file
```

## Development Workflow

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/somegithubuser245/cryptocurrency-tracker.git
cd cryptocurrency-tracker

# Start development with Docker
docker-compose up --build
```

### Testing

```bash
# Backend tests
cd backend
pytest tests/ -v
```

### Key Development Areas

#### 1. Spread Analysis Implementation

- **Location**: `backend/src/routes/scan_spreads.py`
- **Status**: In development
- **Goal**: Implement real-time and historical spread calculations

#### 2. Pair Discovery System

- **Location**: `backend/src/services/external_api_caller.py`
- **Status**: Partially implemented
- **Goal**: Automatic detection of supported pairs across exchanges

#### 3. Frontend Spread Table

- **Location**: `frontend/src/components/` (new component needed)
- **Status**: Planned
- **Goal**: Display sortable spread analysis table

#### 4. WebSocket Integration

- **Location**: Both backend and frontend
- **Status**: Planned
- **Goal**: Real-time spread updates

## Contributing

**see issues for more info**

### Priority Development Tasks

1. **Spread Analysis Table (Frontend)**

   - Create spread analysis table component
   - Implement sorting by 4-hour max spread
   - Add color coding for positive/negative spreads
   - Ensure responsive design

2. **Historical Max Spread Calculation (Backend)**

   - Implement 4-hour maximum spread tracking
   - Integrate with pandas for data processing
   - Add caching for computed spreads

3. **WebSocket Implementation**

   - Set up WebSocket server in FastAPI
   - Implement real-time spread updates
   - Add frontend WebSocket client

4. **Pair Discovery System**
   - Complete automatic pair discovery across exchanges
   - Implement caching for discovered pairs
   - Add pair filtering and management

### Contribution Guidelines

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Follow the project structure** and naming conventions
4. **Commit your changes** (`git commit -m 'Add some amazing feature'`)
5. **Push to the branch** (`git push origin feature/amazing-feature`)
6. **Open a Pull Request**

> Updating docs and writing tests is nice, but not necessary

### Code Quality Standards

- **Backend**: Follow PEP 8, use type hints, add docstrings
- **Frontend**: Use TypeScript, follow React best practices, add proper typing
- **Documentation**: Update README and API docs if necessary

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
