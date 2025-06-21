# Developer Setup & Troubleshooting Guide

## Quick Start

The easiest way to get started:

### Option 1: Using Setup Scripts (Recommended)

**Windows:**
```cmd
scripts\setup.bat
```

**Linux/macOS:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Option 2: Manual Docker Compose

```bash
# Build and start all services
docker-compose build
docker-compose up -d

# View logs
docker-compose logs -f
```

## Common Issues & Solutions

### 1. Kafka Cluster ID Mismatch

**Problem:** You see error like:
```
The Cluster ID _9PUxvuXQdubwDjROX6bkw doesn't match stored clusterId Some(m1PPUtLpQJ6AdVefvkHiaQ)
```

**Solution:** This is automatically handled by the `kafka-cleanup` service in docker-compose.yml. If you still encounter issues:

```bash
# Stop services
docker-compose down

# Remove only Kafka and Zookeeper volumes
docker volume rm cryptocurrency-tracker_kafka-data cryptocurrency-tracker_zookeeper-data

# Restart
docker-compose up -d
```

### 2. Port Conflicts

**Problem:** Services fail to start due to port conflicts.

**Solution:** Check what's using the ports:
```bash
# Check specific ports
netstat -tulpn | grep :9092    # Kafka
netstat -tulpn | grep :5432    # PostgreSQL
netstat -tulpn | grep :6379    # Redis
netstat -tulpn | grep :5173    # Frontend

# Stop conflicting services or change ports in docker-compose.yml
```

### 3. Out of Memory Issues

**Problem:** Services crash with out of memory errors.

**Solution:** Increase Docker memory limits:
- Docker Desktop: Settings → Resources → Memory (recommend 8GB+)
- Or reduce service memory in docker-compose.yml

### 4. Services Won't Start

**Problem:** Services remain in "starting" state.

**Solution:**
```bash
# Check service health
docker-compose ps

# View specific service logs
docker-compose logs [service-name]

# Common service names:
# - zookeeper
# - kafka  
# - redis
# - timescaledb
# - market-data-service
# - arbitrage-detection-service
# - exchange-integration-service
# - frontend
```

## Complete Environment Reset

If you need to start completely fresh:

**Windows:**
```cmd
scripts\clean-reset.bat
```

**Linux/macOS:**
```bash
chmod +x scripts/clean-reset.sh
./scripts/clean-reset.sh
```

## Service Architecture

The system consists of several interconnected services:

### Infrastructure Services
- **Zookeeper**: Kafka coordination
- **Kafka**: Message streaming platform
- **Redis**: Caching and session storage
- **TimescaleDB**: Time-series database for market data

### Application Services
- **Market Data Service** (Port 8001): Collects real-time market data
- **Arbitrage Detection Service** (Port 8002): Identifies trading opportunities
- **Exchange Integration Service** (Port 8003): Handles exchange communications
- **Frontend** (Port 5173): React-based web interface

## Development Workflow

### Starting Development
1. Run setup script or `docker-compose up -d`
2. Wait for all services to be healthy (check with `docker-compose ps`)
3. Access frontend at http://localhost:5173

### Making Changes
- **Backend Services**: Changes are automatically reloaded via volume mounts
- **Frontend**: Vite hot reload is enabled
- **Infrastructure**: Restart specific services: `docker-compose restart [service-name]`

### Database Access
```bash
# Connect to TimescaleDB
docker exec -it arbitrage-timescaledb psql -U postgres -d arbitrage_db

# Connect to Redis
docker exec -it arbitrage-redis redis-cli
```

### Kafka Management
```bash
# List topics
docker exec arbitrage-kafka kafka-topics --bootstrap-server localhost:9092 --list

# View topic details
docker exec arbitrage-kafka kafka-topics --bootstrap-server localhost:9092 --describe --topic price-updates

# Consume messages (for debugging)
docker exec arbitrage-kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic price-updates --from-beginning
```

## Performance Monitoring

### Health Checks
```bash
# Check all service health
docker-compose ps

# Check specific service logs
docker-compose logs -f kafka
docker-compose logs -f market-data-service
```

### Resource Usage
```bash
# Monitor container resource usage
docker stats

# Check volume usage
docker system df
```

## Troubleshooting Checklist

When services fail to start, check in this order:

1. **Docker Resources**: Ensure adequate memory/CPU allocation
2. **Port Conflicts**: Verify no other services are using required ports
3. **Volume Permissions**: Check if Docker has access to project directory
4. **Service Dependencies**: Ensure infrastructure services start before application services
5. **Network Connectivity**: Verify Docker network is properly configured

### Common Error Patterns

**"Connection refused" errors:**
- Service may still be starting up
- Check if dependent services are healthy
- Verify correct port configuration

**"Volume mount" errors:**
- Check Docker file sharing settings
- Ensure proper permissions on project directory

**"Out of memory" errors:**
- Increase Docker memory allocation
- Reduce service resource requirements

## Environment Variables

Key environment variables that can be customized:

```yaml
# Database
POSTGRES_PASSWORD: arbitrage_password_2025
POSTGRES_DB: arbitrage_db

# Kafka
KAFKA_BOOTSTRAP_SERVERS: kafka:29092

# Redis
REDIS_URL: redis://redis:6379

# Frontend
VITE_API_BASE_URL: http://localhost
```

## Production Considerations

For production deployment:

1. **Security**: Change default passwords and add authentication
2. **Scaling**: Increase replication factors and partition counts
3. **Monitoring**: Add proper logging and metrics collection
4. **Persistence**: Ensure volume backups for critical data
5. **Load Balancing**: Add reverse proxy for application services

## Getting Help

If you encounter issues not covered here:

1. Check service logs: `docker-compose logs [service-name]`
2. Verify service health: `docker-compose ps`
3. Try clean reset: `./scripts/clean-reset.sh`
4. Check Docker system: `docker system df` and `docker system prune`

## Development Tips

- Use `docker-compose logs -f` to monitor all services in real-time
- The `kafka-cleanup` service automatically handles cluster ID mismatches
- Database data persists between restarts (unless volumes are removed)
- Frontend supports hot reload for rapid development
- All application services support live code reloading
