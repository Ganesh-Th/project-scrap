# AI Review Intelligence System

This system analyzes app reviews using AI to provide actionable insights.

## Quick Start

See the main README.md for detailed setup instructions.

### Development Setup

1. Start PostgreSQL and Redis:
   ```bash
   docker-compose up -d postgres redis
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations (automatic on startup)

4. Start FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Start Celery worker:
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

## Environment Variables

Copy `.env.example` to `.env` and configure:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SERPAPI_KEY`: Your SerpAPI key (use "demo_key" for demo mode)

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.
