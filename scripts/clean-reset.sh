#!/bin/bash

# Cryptocurrency Arbitrage Detection System - Clean Reset Script
# This script completely resets the development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

echo "🧹 Cryptocurrency Arbitrage Detection System - Clean Reset"
echo ""

print_warning "This will completely reset your development environment:"
print_warning "- Stop and remove all containers"
print_warning "- Remove all project volumes (including database data)"
print_warning "- Remove all project images"
print_warning "- Clean up networks"
echo ""

read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Reset cancelled"
    exit 0
fi

# Stop and remove containers
print_status "Stopping and removing containers..."
docker-compose down --remove-orphans

# Remove volumes
print_status "Removing project volumes..."
docker volume ls -q | grep "cryptocurrency-tracker" | xargs -r docker volume rm

# Remove images
print_status "Removing project images..."
docker images --format "table {{.Repository}}" | grep "cryptocurrency-tracker" | xargs -r docker rmi -f

# Remove networks
print_status "Cleaning up networks..."
docker network ls -q --filter "name=arbitrage" | xargs -r docker network rm

# Clean up any dangling resources
print_status "Cleaning up dangling resources..."
docker system prune -f

print_success "Environment reset complete!"
print_status "You can now run './scripts/setup.sh' to start fresh"
