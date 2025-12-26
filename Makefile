.PHONY: help start stop restart logs health clean install-backend install-frontend test

help: ## Show this help message
	@echo "AI Review Intelligence System - Make Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

start: ## Start all services with Docker Compose
	@echo "🚀 Starting AI Review Intelligence System..."
	@if [ ! -f .env ]; then cp .env.example .env; fi
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend:  http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

stop: ## Stop all services
	@echo "🛑 Stopping services..."
	docker-compose down
	@echo "✅ Services stopped!"

restart: stop start ## Restart all services

logs: ## Show logs from all services
	docker-compose logs -f

health: ## Check health of all services
	@./health-check.sh

clean: ## Stop services and remove volumes
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	@echo "✅ Cleanup complete!"

install-backend: ## Install backend dependencies
	@echo "📦 Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "✅ Backend dependencies installed!"

install-frontend: ## Install frontend dependencies
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Frontend dependencies installed!"

test: ## Run tests
	@echo "🧪 Running tests..."
	@echo "Backend tests:"
	cd backend && python -m pytest || true
	@echo ""
	@echo "Frontend tests:"
	cd frontend && npm test || true

dev-backend: ## Run backend in development mode
	cd backend && uvicorn app.main:app --reload

dev-frontend: ## Run frontend in development mode
	cd frontend && npm run dev

dev-worker: ## Run Celery worker in development mode
	cd backend && celery -A app.celery_app worker --loglevel=info

build: ## Build Docker images
	docker-compose build

rebuild: ## Rebuild Docker images without cache
	docker-compose build --no-cache

ps: ## Show running services
	docker-compose ps

shell-backend: ## Open shell in backend container
	docker-compose exec backend /bin/bash

shell-db: ## Open PostgreSQL shell
	docker-compose exec postgres psql -U postgres -d review_intelligence

shell-redis: ## Open Redis CLI
	docker-compose exec redis redis-cli
