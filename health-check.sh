#!/bin/bash

# Health check script for the AI Review Intelligence System

echo "🏥 Health Check - AI Review Intelligence System"
echo ""

# Check Docker services
echo "Checking Docker services..."
docker-compose ps

echo ""

# Check Backend API
echo "Checking Backend API..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✓ Backend API is healthy"
    curl -s http://localhost:8000/health | python3 -m json.tool
else
    echo "❌ Backend API is not responding"
fi

echo ""

# Check Frontend
echo "Checking Frontend..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✓ Frontend is responding"
else
    echo "❌ Frontend is not responding"
fi

echo ""

# Check PostgreSQL
echo "Checking PostgreSQL..."
if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "✓ PostgreSQL is ready"
else
    echo "❌ PostgreSQL is not ready"
fi

echo ""

# Check Redis
echo "Checking Redis..."
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✓ Redis is responding"
else
    echo "❌ Redis is not responding"
fi

echo ""
echo "Health check complete!"
