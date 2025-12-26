# AI Review Intelligence System

A full-stack web application that ingests and analyzes app reviews using AI-powered sentiment analysis, multi-label classification, clustering, and task prioritization with RICE scoring.

## Features

### Backend (FastAPI + Celery + Redis + PostgreSQL)
- **Asynchronous Review Ingestion**: Fetches app reviews via SerpAPI (with demo mode)
- **Job State Tracking**: Monitors job progress through states: `queued` → `fetching` → `analyzing` → `clustering` → `done`
- **AI-Powered Analysis**:
  - Sentiment Analysis (positive/negative/neutral)
  - Multi-label Classification (bug, feature, usability, requirement, praise)
  - Review Clustering into themes
- **Task Generation**: Automatically converts themes into actionable tasks
- **RICE Prioritization**: Calculate and adjust priority scores (Reach × Impact × Confidence / Effort)
- **User Confirmation**: Approve or reject generated tasks

### Frontend (Next.js + TypeScript)
- **Modern Dashboard**: Clean, responsive UI with real-time updates
- **Job Management**: Create and monitor analysis jobs
- **Results Visualization**: View sentiment stats, themes, and tasks
- **Interactive Prioritization**: Edit RICE scores and confirm tasks
- **Live Updates**: Auto-refresh for in-progress jobs

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Next.js   │─────▶│   FastAPI    │─────▶│  PostgreSQL │
│  Frontend   │      │   Backend    │      │  Database   │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │    Redis     │
                     │   + Celery   │
                     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  SerpAPI /   │
                     │  Mock Data   │
                     └──────────────┘
```

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- (Optional) SerpAPI key for real data

### Option 1: Using Start Script (Recommended)

```bash
# Clone the repository
git clone https://github.com/Ganesh-Th/project-scrap.git
cd project-scrap

# Start everything with one command
./start.sh

# Or using Make
make start
```

### Option 2: Using Docker Compose Directly

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Ganesh-Th/project-scrap.git
   cd project-scrap
   ```

2. **Set up environment** (optional):
   ```bash
   # Copy example env file
   cp .env.example .env
   # Edit if needed (default uses demo mode)
   ```

3. **Start all services**:
   ```bash
   docker-compose up -d
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

5. **Check health**:
   ```bash
   ./health-check.sh
   # Or: make health
   ```

### Manual Setup (Development)

#### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Start services** (PostgreSQL and Redis):
   ```bash
   docker-compose up -d postgres redis
   ```

6. **Run FastAPI server**:
   ```bash
   uvicorn app.main:app --reload
   ```

7. **Run Celery worker** (in another terminal):
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

#### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment**:
   ```bash
   cp .env.local.example .env.local
   ```

4. **Run development server**:
   ```bash
   npm run dev
   ```

## Usage

### Quick Test

1. **Start the system** (if not already running):
   ```bash
   make start  # or ./start.sh
   ```

2. **Open the dashboard**: http://localhost:3000

3. **Create your first analysis**:
   - Enter app name: "Test App"
   - Enter app ID: "com.test.app"
   - Click "Start Analysis"

4. **Watch the progress**:
   - Job moves through: queued → fetching → analyzing → clustering → done
   - Takes about 10-30 seconds

5. **View results**:
   - Sentiment analysis
   - Review categories
   - Themes and tasks with RICE scores

For detailed testing instructions, see [TESTING.md](TESTING.md).

### Using the Dashboard

1. **Create a New Analysis Job**:
   - Enter an app name (e.g., "My App")
   - Enter an app ID/package name (e.g., "com.example.app")
   - Click "Start Analysis"

2. **Monitor Progress**:
   - Watch the job progress through different states
   - The system will automatically fetch, analyze, and cluster reviews

3. **View Results**:
   - See sentiment distribution and average rating
   - Explore identified themes and generated tasks
   - Review sample classified reviews

4. **Prioritize Tasks**:
   - Edit RICE scores for each task
   - Confirm or reject generated tasks
   - Tasks are automatically ranked by RICE score

## API Endpoints

### Jobs
- `POST /api/jobs` - Create new analysis job
- `GET /api/jobs` - List all jobs
- `GET /api/jobs/{id}` - Get job details
- `GET /api/jobs/{id}/results` - Get job results with reviews and themes
- `GET /api/jobs/{id}/reviews` - Get job reviews
- `GET /api/jobs/{id}/themes` - Get job themes

### Tasks
- `GET /api/tasks/{id}` - Get task details
- `PUT /api/tasks/{id}` - Update task (RICE scores, confirmation)

## Demo Mode

The system includes a demo mode that generates mock reviews when `SERPAPI_KEY=demo_key`. This allows you to test the system without an actual SerpAPI key.

Mock reviews include various scenarios:
- Bug reports
- Feature requests
- Usability feedback
- User praise
- Different sentiment levels

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **Celery**: Distributed task queue
- **Redis**: Message broker and result backend
- **PostgreSQL**: Primary database
- **Transformers**: NLP models for sentiment analysis
- **scikit-learn**: Clustering algorithms

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client
- **Lucide React**: Icon library

## Project Structure

```
project-scrap/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   ├── tasks/         # Celery tasks
│   │   ├── config.py      # Configuration
│   │   ├── database.py    # Database setup
│   │   ├── celery_app.py  # Celery configuration
│   │   └── main.py        # FastAPI application
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js app directory
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities
│   │   └── types/         # TypeScript types
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## Development

For development setup and contributing guidelines, see:
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [TESTING.md](TESTING.md) - Testing guide
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment

### Quick Commands

```bash
make start          # Start all services
make stop           # Stop all services
make logs           # View logs
make health         # Check health
make clean          # Clean up everything
make help           # Show all commands
```

### Adding New Features

1. **Backend**: Add new endpoints in `backend/app/api/`
2. **Frontend**: Create components in `frontend/src/components/`
3. **Database**: Modify models in `backend/app/models/`
4. **Tasks**: Add Celery tasks in `backend/app/tasks/`

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.