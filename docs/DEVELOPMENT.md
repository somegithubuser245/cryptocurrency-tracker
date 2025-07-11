# Development Runner

A cross-platform Python script to manage the entire Cryptocurrency Tracker application stack.

## Quick Start

### Prerequisites Check
```bash
python run.py --check
```

### Development Mode (Recommended)
```bash
# Full Docker stack with hot-reload
python run.py dev

# OR using npm
npm run start
```

### Local Development (No Docker)
```bash
# Run services locally
python run.py local

# OR using npm
npm run start:local
```

### Production Mode
```bash
# Build and run production stack
python run.py prod

# OR using npm
npm run start:prod
```

## Available Commands

| Command  | Description            | Docker | Hot Reload |
|----------|------------------------|--------|------------|
| `dev`    | Full development stack | ✅      | ✅          |
| `local`  | Local development      | ❌      | ✅          |
| `prod`   | Production build       | ✅      | ❌          |
| `build`  | Build frontend only    | ❌      | ❌          |
| `status` | Show service status    | -      | -          |
| `stop`   | Stop all services      | -      | -          |

## Development URLs

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Redis**: localhost:6379

## Features

### ✅ System Agnostic
- Works on Windows, macOS, and Linux
- Automatic prerequisite checking
- Cross-platform process management

### ✅ Multiple Run Modes
- **Docker**: Full containerized stack
- **Local**: Native development environment
- **Production**: Optimized production build

### ✅ Smart Management
- Automatic dependency installation
- Graceful shutdown (Ctrl+C)
- Process cleanup and monitoring
- Service status checking

### ✅ Hot Module Replacement
- Frontend: Vite HMR for instant updates
- Backend: uvicorn auto-reload for API changes
- Real-time development experience

## Prerequisites

### Required
- **Python 3.7+**: Script runner
- **Docker & Docker Compose**: Container orchestration

### Optional (for local mode)
- **Node.js 18+**: Frontend development
- **Redis**: Caching (auto-managed via Docker if missing)

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Frontend     │    │     Backend     │    │      Redis      │
│   (React/Vite)  │    │  (FastAPI/Python│    │    (Caching)    │
│   Port: 5173    │◄──►│   Port: 8000    │◄──►│   Port: 6379    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Troubleshooting

### Docker Issues
```bash
# Check Docker status
docker --version
docker compose version

# Reset containers
python run.py stop
docker system prune -f
```

### Port Conflicts
- Frontend (5173): Change in `frontend/vite.config.ts`
- Backend (8000): Change in `backend/src/routes/main.py`
- Redis (6379): Change in `docker-compose.yml`

### Permission Issues (Linux/macOS)
```bash
chmod +x run.py
sudo usermod -aG docker $USER  # Add user to docker group
```

## NPM Convenience Scripts

All commands are also available via npm:

```bash
npm run start          # python run.py dev
npm run start:local    # python run.py local  
npm run start:prod     # python run.py prod
npm run stop           # python run.py stop
npm run status         # python run.py status
npm run check          # python run.py --check
```

## Environment Variables

Create `.env` files for environment-specific configuration:

### Backend `.env`
```env
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
```

### Frontend `.env`
```env
VITE_API_BASE_URL=http://localhost:8000
```

## Development Workflow

1. **Initial Setup**
   ```bash
   git clone <repository>
   cd cryptocurrency-tracker
   python run.py --check
   ```

2. **Daily Development**
   ```bash
   python run.py dev
   # Code, test, repeat...
   # Ctrl+C to stop
   ```

3. **Production Testing**
   ```bash
   python run.py prod
   ```

4. **Service Management**
   ```bash
   python run.py status  # Check what's running
   python run.py stop    # Stop everything
   ```

## Performance Notes

- **Docker mode**: Slower startup, consistent environment
- **Local mode**: Faster startup, requires local tools
- **HMR**: Both modes support hot reloading for rapid development
- **Build caching**: Docker builds are cached for faster subsequent runs
