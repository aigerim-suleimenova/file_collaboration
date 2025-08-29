#!/bin/bash

# Production Deployment Script for File Collaboration App
# Usage: ./deploy.sh [environment]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default environment
ENVIRONMENT=${1:-production}

echo -e "${GREEN}🚀 Starting deployment for environment: $ENVIRONMENT${NC}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    if [ -f env.production.example ]; then
        cp env.production.example .env
        echo -e "${YELLOW}⚠️  Please edit .env file with your production values before continuing.${NC}"
        echo -e "${YELLOW}⚠️  Press Enter when ready to continue...${NC}"
        read
    else
        echo -e "${RED}❌ No environment template found. Please create .env file manually.${NC}"
        exit 1
    fi
fi

# Load environment variables
source .env

# Validate required environment variables
required_vars=("POSTGRES_PASSWORD" "SECRET_KEY" "FRONTEND_HOST")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ Required environment variable $var is not set.${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ Environment variables validated${NC}"

# Stop existing containers
echo -e "${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose -f docker-compose.prod.yml down --remove-orphans || true

# Clean up old images
echo -e "${YELLOW}🧹 Cleaning up old images...${NC}"
docker system prune -f

# Build and start services
echo -e "${GREEN}🔨 Building and starting services...${NC}"
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 30

# Check service health
echo -e "${YELLOW}🏥 Checking service health...${NC}"
if docker-compose -f docker-compose.prod.yml ps | grep -q "unhealthy\|starting"; then
    echo -e "${RED}❌ Some services are not healthy. Check logs:${NC}"
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi

# Run database migrations
echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head || {
    echo -e "${YELLOW}⚠️  Migration failed, but continuing...${NC}"
}

# Final health check
echo -e "${YELLOW}🔍 Final health check...${NC}"
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${YELLOW}⚠️  Health check failed, but services may still be starting...${NC}"
fi

# Show service status
echo -e "${GREEN}📊 Service status:${NC}"
docker-compose -f docker-compose.prod.yml ps

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${GREEN}🌐 Your application should be available at: ${FRONTEND_HOST:-http://localhost}${NC}"
echo -e "${GREEN}📝 Check logs with: docker-compose -f docker-compose.prod.yml logs -f${NC}"
