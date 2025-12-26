#!/bin/bash

# Startup script for AI Review Intelligence System

set -e

echo "🚀 Starting AI Review Intelligence System..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    echo "SERPAPI_KEY=demo_key" > .env
    echo "✓ .env file created with demo key"
fi

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

echo ""
echo "✨ AI Review Intelligence System is starting!"
echo ""
echo "Services:"
echo "  - Frontend:  http://localhost:3000"
echo "  - Backend:   http://localhost:8000"
echo "  - API Docs:  http://localhost:8000/docs"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
