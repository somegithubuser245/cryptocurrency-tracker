#!/bin/bash

# Cryptocurrency Arbitrage Detection System - Setup Script
# This script provides a graceful way to start the system, handling common issues

set -e

echo "🚀 Starting Cryptocurrency Arbitrage Detection System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_success "Docker is running"

# Check for existing containers and handle gracefully
if docker ps -a --format "table {{.Names}}" | grep -q "arbitrage-"; then
    print_warning "Found existing arbitrage containers"
    read -p "Do you want to stop and remove existing containers? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Stopping and removing existing containers..."
        docker-compose down
    fi
fi

# Build and start services
print_status "Building and starting services..."
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be healthy
print_status "Waiting for services to become healthy..."

# Function to wait for service
wait_for_service() {
    local service_name=$1
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps --services --filter "status=running" | grep -q "$service_name"; then
            if [ "$service_name" = "kafka" ] || [ "$service_name" = "redis" ] || [ "$service_name" = "timescaledb" ]; then
                # Check health status for infrastructure services
                health_status=$(docker inspect --format='{{.State.Health.Status}}' "arbitrage-$service_name" 2>/dev/null || echo "none")
                if [ "$health_status" = "healthy" ]; then
                    print_success "$service_name is healthy"
                    return 0
                fi
            else
                print_success "$service_name is running"
                return 0
            fi
        fi
        
        print_status "Waiting for $service_name... (attempt $attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done
    
    print_error "$service_name failed to become healthy"
    return 1
}

# Wait for infrastructure services
wait_for_service "zookeeper"
wait_for_service "kafka"
wait_for_service "redis"
wait_for_service "timescaledb"

# Wait for application services
wait_for_service "market-data-service"
wait_for_service "arbitrage-detection-service"
wait_for_service "exchange-integration-service"
wait_for_service "frontend"

print_success "All services are running!"

# Display service URLs
echo ""
echo "🌐 Service URLs:"
echo "  Frontend:                 http://localhost:5173"
echo "  Market Data Service:      http://localhost:8001"
echo "  Arbitrage Detection:      http://localhost:8002"
echo "  Exchange Integration:     http://localhost:8003"
echo "  TimescaleDB:             postgresql://postgres:arbitrage_password_2025@localhost:5432/arbitrage_db"
echo "  Redis:                   redis://localhost:6379"
echo "  Kafka:                   localhost:9092"
echo ""

# Show logs for debugging
echo "📋 To view logs:"
echo "  All services:    docker-compose logs -f"
echo "  Specific service: docker-compose logs -f [service-name]"
echo ""

echo "🎉 System is ready for development!"
