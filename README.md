# Multi-Source Review Scraper API

A production-ready FastAPI application for scraping app reviews from multiple sources and performing AI-powered sentiment analysis using Google Gemini.

## ✨ Features

- **Multi-Source Scraping**: Google Play Store, Apple App Store, Reddit, Google Search
- **AI Sentiment Analysis**: Powered by Google Gemini with URL context and social media search
- **Real-time Progress**: WebSocket updates for task monitoring
- **Task Persistence**: Redis-backed task storage with 24-hour TTL
- **Task Prioritization**: MoSCoW and Lean prioritization frameworks
- **Async Architecture**: Non-blocking I/O with `httpx` and `asyncio`

## 🏗️ Architecture

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

1. **Clone and navigate to the project:**
   ```bash
   cd project-scrap
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
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
| POST | `/api/v1/scrape` | Start multi-source scrape task |
| GET | `/api/v1/task/{task_id}` | Get task status and result |
| POST | `/api/v1/prioritize` | Prioritize findings from analysis |
| WS | `/ws/task/{task_id}` | WebSocket for real-time progress |

### Single-Source Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/scrape/google-play` | Google Play only |
| POST | `/api/v1/scrape/apple-store` | Apple Store only |
| POST | `/api/v1/scrape/reddit` | Reddit only |
| POST | `/api/v1/scrape/google-search` | Google Search only |

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

### WebSocket Progress (JavaScript)

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/task/abc123-def456');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Progress: ${data.progress}% - ${data.message}`);
  
  if (data.status === 'completed') {
    console.log('Task completed! Fetch results...');
    ws.close();
  }
};
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

## 📊 Analysis Output

The AI categorizes findings into 7 types:

| Type | Description |
|------|-------------|
| `bug` | Technical issues, crashes, errors |
| `feature_request` | User-requested new features |
| `requirement` | Must-have missing features |
| `usability_friction` | UX issues causing frustration |
| `pain_point` | General user dissatisfaction |
| `positive_review` | Things users love |
| `ai_insight` | AI-discovered patterns |

## ⚙️ Configuration

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `SERPAPI_KEY` | - | SerpAPI key (required) |
| `GEMINI_API_KEY` | - | Google Gemini key (required) |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `DEBUG` | `false` | Enable debug mode |

## 🔮 Future Enhancements

These features are documented for future implementation:

1. **Docker & Compose**: Containerized deployment
2. **pytest Suite**: Unit and integration tests
3. **GitHub Actions CI**: Automated testing and linting
4. **API Key Authentication**: Secure endpoint access
5. **Nginx Reverse Proxy**: Production deployment
6. **Custom OpenAPI Spec**: Enhanced documentation

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

Built with ❤️ using FastAPI, Redis, and Google Gemini
