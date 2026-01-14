# Backend - Sentiment to Sprint API

A production-ready FastAPI application for scraping app reviews from multiple sources and performing AI-powered sentiment analysis using Google Gemini.

> 📖 For product overview and vision, see the [Main README](../README.md)

## ✨ Features

- **Multi-Source Scraping**: Google Play Store, Apple App Store, Reddit, Google Search
- **AI Sentiment Analysis**: Powered by Google Gemini with URL context and social media search
- **Real-time Progress**: WebSocket updates for task monitoring
- **Task Persistence**: Redis-backed task storage with 24-hour TTL
- **Task Prioritization**: MoSCoW and Lean prioritization frameworks
- **Async Architecture**: Non-blocking I/O with `httpx` and `asyncio`

---

## 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.10+** | Core language |
| **FastAPI** | High-performance async web framework |
| **Pydantic v2** | Data validation and serialization |
| **Redis** | Task queue and result caching |
| **httpx** | Async HTTP client for scraping |
| **BeautifulSoup4** | HTML parsing for Reddit |
| **Google Gemini** | AI sentiment analysis |
| **SerpAPI** | Google/App Store data extraction |
| **WebSockets** | Real-time progress updates |
| **Uvicorn** | ASGI server |

### DevOps & Tools

| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization (planned) |
| **Railway** | Backend deployment |
| **Git** | Version control |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Next.js)                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ AnalysisForm│  │ProgressModal│  │ ResultsView │  │PrioritizationResults│ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         │                │                │                     │            │
│         └────────────────┴────────────────┴─────────────────────┘            │
│                                    │                                          │
│                          ┌─────────▼─────────┐                               │
│                          │    API Client     │                               │
│                          │  (lib/api.ts)     │                               │
│                          └─────────┬─────────┘                               │
└────────────────────────────────────┼─────────────────────────────────────────┘
                                     │ REST API / WebSocket
┌────────────────────────────────────┼─────────────────────────────────────────┐
│                              BACKEND (FastAPI)                               │
│                          ┌─────────▼─────────┐                               │
│                          │   API Endpoints   │                               │
│                          │ (scraper.py)      │                               │
│                          └─────────┬─────────┘                               │
│                                    │                                          │
│    ┌───────────────────────────────┼───────────────────────────────┐         │
│    │                               │                               │         │
│    ▼                               ▼                               ▼         │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐│
│ │Google    │  │Apple     │  │Reddit    │  │Google    │  │  Prioritization  ││
│ │Play      │  │Store     │  │Scraper   │  │Search    │  │  Engine          ││
│ │Scraper   │  │Scraper   │  │(httpx)   │  │Scraper   │  │  (MoSCoW/Lean)   ││
│ │(SerpAPI) │  │(SerpAPI) │  │          │  │(SerpAPI) │  │                  ││
│ └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘│
│      │             │             │             │                  │          │
│      └─────────────┴─────────────┴─────────────┘                  │          │
│                          │                                        │          │
│                ┌─────────▼─────────┐                             │          │
│                │   Data Processor  │                             │          │
│                │   (Aggregation)   │                             │          │
│                └─────────┬─────────┘                             │          │
│                          │                                        │          │
│                ┌─────────▼─────────┐              ┌──────────────▼────────┐ │
│                │  Gemini AI        │              │       Redis           │ │
│                │  Sentiment Engine │◄─────────────►  Task Storage         │ │
│                └───────────────────┘              │  (24hr TTL)           │ │
│                                                   └───────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
            ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
            │ Google Play │  │ App Store   │  │   Reddit    │
            │   API       │  │   API       │  │   Website   │
            └─────────────┘  └─────────────┘  └─────────────┘
```

---

## 📁 Project Structure

```
app/
├── api/v1/endpoints/      # API route handlers
│   └── scraper.py         # Main scraper endpoints
├── core/                  # Core infrastructure
│   ├── redis_store.py     # Redis task persistence
│   └── connection_manager.py  # WebSocket management
├── models/                # Pydantic data models
│   ├── requests.py        # Request validation
│   └── responses.py       # Response schemas
├── services/              # Business logic
│   ├── google_play.py     # Google Play scraper
│   ├── apple_store.py     # Apple Store scraper
│   ├── reddit.py          # Async Reddit scraper
│   ├── google_search.py   # Google Search scraper
│   ├── sentiment.py       # Gemini sentiment analysis
│   ├── data_processor.py  # TOON format conversion
│   └── prioritization.py  # Task prioritization
├── utils/                 # Utility functions
│   ├── constants.py       # Country mappings, user agents
│   └── helpers.py         # Helper functions
├── config.py              # Pydantic Settings configuration
├── logging_config.py      # Logging setup
└── main.py                # FastAPI app initialization
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Redis server (local or remote)
- API keys: SerpAPI, Google Gemini

### Installation

1. **Navigate to the project root:**
   ```bash
   cd project-scrap
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Activate on Windows
   .\venv\Scripts\activate
   
   # Activate on Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Start Redis:** (if not running)
   ```bash
   # Using Docker
   docker run -d -p 6379:6379 redis:alpine
   
   # Or install Redis locally
   ```

6. **Run the application:**
   ```bash
   python run.py
   ```

7. **Access the API:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Health: http://localhost:8000/health

## 📡 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/scrape` | Start multi-source scrape task |
| `GET` | `/api/v1/task/{task_id}` | Get task status and result |
| `POST` | `/api/v1/prioritize` | Prioritize findings from analysis |
| `WS` | `/ws/task/{task_id}` | WebSocket for real-time progress |

### Single-Source Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/scrape/google-play` | Google Play only |
| `POST` | `/api/v1/scrape/apple-store` | Apple Store only |
| `POST` | `/api/v1/scrape/reddit` | Reddit only |
| `POST` | `/api/v1/scrape/google-search` | Google Search only |

## 🔧 Usage Examples

### Start a Multi-Source Scrape

```bash
curl -X POST http://localhost:8000/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "YouTube",
    "google_play": {
      "product_id": "com.google.android.youtube",
      "platform": "phone"
    },
    "apple_store": {
      "product_id": "544007664",
      "country": "us"
    },
    "include_reddit": true,
    "include_google_search": true
  }'
```

**Response:**
```json
{
  "task_id": "abc123-def456",
  "status": "pending",
  "message": "Scraping task started for sources: google_play_store, apple_app_store, reddit, google_search",
  "websocket_url": "/ws/task/abc123-def456"
}
```

### Check Task Status

```bash
curl http://localhost:8000/api/v1/task/abc123-def456
```

### Prioritize Tasks

```bash
curl -X POST http://localhost:8000/api/v1/prioritize \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "abc123-def456",
    "method": "MoSCoW",
    "duration": 14,
    "budget": 160,
    "business_goal": "Improve user retention"
  }'
```

## 📊 Analysis Output Categories

The AI categorizes findings into 7 actionable types:

| Type | Icon | Description | Example |
|------|------|-------------|---------|
| `bug` | 🐛 | Technical issues, crashes, errors | "App crashes when uploading photos" |
| `feature_request` | ✨ | User-requested new features | "Please add dark mode" |
| `requirement` | 📋 | Must-have missing features | "Need offline support" |
| `usability_friction` | 🔧 | UX issues causing frustration | "Navigation is confusing" |
| `pain_point` | 😤 | General user dissatisfaction | "Too many ads" |
| `positive_review` | ⭐ | Things users love | "Best app for podcasts!" |
| `ai_insight` | 🤖 | AI-discovered patterns | "30% of users mention slow loading" |

---

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERPAPI_KEY` | - | SerpAPI key (required) |
| `GEMINI_API_KEY` | - | Google Gemini key (required) |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `DEBUG` | `false` | Enable debug mode |

## 🔗 Related

- [Frontend Documentation](../frontend/README.md) - Next.js UI application
- [Main README](../README.md) - Product overview and vision

---

## 🎓 Skills Demonstrated

This backend showcases proficiency in:

### Backend Development
- ✅ Building RESTful APIs with FastAPI
- ✅ Async/await patterns with Python asyncio
- ✅ WebSocket implementation for real-time updates
- ✅ Data validation with Pydantic v2
- ✅ Redis integration for caching and persistence
- ✅ External API integration (SerpAPI, Gemini)
- ✅ Web scraping with httpx and BeautifulSoup

### System Design
- ✅ Microservices architecture
- ✅ Async task processing
- ✅ Real-time communication patterns
- ✅ Caching strategies
- ✅ Clean code and separation of concerns

### AI/ML Integration
- ✅ LLM integration (Google Gemini)
- ✅ Prompt engineering for sentiment analysis
- ✅ Structured output parsing

---

Built with ❤️ using FastAPI, Redis, and Google Gemini
