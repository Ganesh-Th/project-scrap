# 🔍 Review Sentiment Analyzer

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=for-the-badge&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-5.0+-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.0-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)

**A full-stack AI-powered application for scraping app reviews from multiple sources, performing sentiment analysis, and generating prioritized product backlogs.**

[Features](#-features) • [Tech Stack](#-tech-stack) • [Architecture](#-system-architecture) • [Quick Start](#-quick-start) • [API Docs](#-api-documentation) • [Screenshots](#-screenshots)

</div>

---

## 🎯 Project Overview

This project solves the challenge of **understanding user sentiment at scale** by aggregating reviews from multiple platforms, analyzing them with AI, and converting insights into actionable product tasks.

### The Problem
- Product teams spend hours manually reading reviews across platforms
- Reviews are scattered across Google Play, App Store, Reddit, and forums
- Difficult to identify patterns and prioritize what to fix first

### The Solution
An end-to-end pipeline that:
1. **Scrapes** reviews from 4+ sources concurrently
2. **Analyzes** sentiment using Google Gemini AI
3. **Categorizes** findings (bugs, features, pain points, etc.)
4. **Prioritizes** tasks using MoSCoW or Lean methodologies
5. **Generates** a sprint-ready product backlog

---

## ✨ Features

### 🔄 Multi-Source Data Aggregation
- **Google Play Store** - App reviews with ratings, dates, and user info
- **Apple App Store** - iOS app reviews across 40+ countries
- **Reddit** - Subreddit discussions and user feedback
- **Google Search** - Web results for broader sentiment context

### 🤖 AI-Powered Analysis
- **Google Gemini Integration** - Advanced LLM for sentiment analysis
- **Smart Categorization** - 7 finding types (bugs, features, pain points, etc.)
- **Pattern Recognition** - AI-discovered insights from review clusters
- **Confidence Scoring** - Reliability metrics for each finding

### ⚡ Real-Time Processing
- **WebSocket Updates** - Live progress streaming to frontend
- **Async Architecture** - Non-blocking concurrent scraping
- **Task Persistence** - Redis-backed with 24-hour TTL
- **Progress Tracking** - Granular status updates per source

### 📋 Product Prioritization
- **MoSCoW Framework** - Must/Should/Could/Won't categorization
- **Lean Methodology** - Value vs. effort scoring
- **Sprint Planning** - Budget and duration constraints
- **Actionable Backlog** - Ready-to-use task descriptions

### 🎨 Modern Frontend
- **Responsive UI** - Works on desktop and mobile
- **Dark/Light Theme** - Custom purple brand theme
- **Interactive Results** - Expandable categories and findings
- **Real-Time Feedback** - Progress bars and status updates

---

## 🛠 Tech Stack

### Backend
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

### Frontend
| Technology | Purpose |
|------------|---------|
| **Next.js 16** | React framework with App Router |
| **TypeScript** | Type-safe JavaScript |
| **Tailwind CSS v4** | Utility-first styling |
| **shadcn/ui** | Accessible component library |
| **React Hooks** | State management |

### DevOps & Tools
| Technology | Purpose |
|------------|---------|
| **Docker** | Containerization (planned) |
| **Vercel** | Frontend deployment |
| **Railway** | Backend deployment |
| **Git** | Version control |

---

## 🏗 System Architecture

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
project-scrap/
├── app/                          # 🐍 BACKEND (FastAPI)
│   ├── api/v1/endpoints/         # API route handlers
│   │   └── scraper.py            # Main scraper endpoints
│   ├── core/                     # Core infrastructure
│   │   ├── redis_store.py        # Redis task persistence
│   │   └── connection_manager.py # WebSocket management
│   ├── models/                   # Pydantic data models
│   │   ├── requests.py           # Request validation
│   │   └── responses.py          # Response schemas
│   ├── services/                 # Business logic
│   │   ├── google_play.py        # Google Play scraper
│   │   ├── apple_store.py        # Apple Store scraper
│   │   ├── reddit.py             # Async Reddit scraper
│   │   ├── google_search.py      # Google Search scraper
│   │   ├── sentiment.py          # Gemini sentiment analysis
│   │   ├── data_processor.py     # Data aggregation
│   │   └── prioritization.py     # Task prioritization
│   ├── utils/                    # Utility functions
│   ├── config.py                 # Pydantic Settings
│   └── main.py                   # FastAPI app
│
├── frontend/                     # ⚛️ FRONTEND (Next.js)
│   ├── src/
│   │   ├── app/                  # App Router pages
│   │   ├── components/           # React components
│   │   │   ├── ui/               # shadcn/ui components
│   │   │   ├── AnalysisForm.tsx
│   │   │   ├── ResultsView.tsx
│   │   │   └── ...
│   │   ├── hooks/                # Custom React hooks
│   │   ├── lib/                  # API client & utils
│   │   └── types/                # TypeScript interfaces
│   └── package.json
│
├── logs/                         # Application logs
├── requirements.txt              # Python dependencies
├── run.py                        # Backend entry point
└── README.md                     # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Redis server
- API keys: SerpAPI, Google Gemini

### Backend Setup

```bash
# Clone repository
git clone https://github.com/yourusername/review-sentiment-analyzer.git
cd review-sentiment-analyzer

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start Redis (Docker)
docker run -d -p 6379:6379 redis:alpine

# Run backend
python run.py
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Configure environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
```

### Access the Application

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

---

## 📡 API Documentation

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

### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Spotify",
    "google_play": {
      "product_id": "com.spotify.music",
      "platform": "phone"
    },
    "apple_store": {
      "product_id": "324684580",
      "country": "us"
    },
    "include_reddit": true,
    "include_google_search": true
  }'
```

---

## 📊 Analysis Categories

The AI categorizes findings into 7 actionable types:

| Type | Icon | Description | Example |
|------|------|-------------|---------|
| `bug` | 🐛 | Technical issues, crashes | "App crashes when uploading photos" |
| `feature_request` | ✨ | User-requested features | "Please add dark mode" |
| `requirement` | 📋 | Must-have missing features | "Need offline support" |
| `usability_friction` | 🔧 | UX issues | "Navigation is confusing" |
| `pain_point` | 😤 | User frustrations | "Too many ads" |
| `positive_review` | ⭐ | Things users love | "Best app for podcasts!" |
| `ai_insight` | 🤖 | AI-discovered patterns | "30% of users mention slow loading" |

---

## 📸 Screenshots

> *Add screenshots of your application here*

| Analysis Form | Results View | Prioritization |
|---------------|--------------|----------------|
| Step 1 form | Categorized findings | Sprint backlog |

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SERPAPI_KEY` | ✅ | - | SerpAPI key for scraping |
| `GEMINI_API_KEY` | ✅ | - | Google Gemini API key |
| `REDIS_URL` | ❌ | `redis://localhost:6379` | Redis connection URL |
| `HOST` | ❌ | `0.0.0.0` | Server host |
| `PORT` | ❌ | `8000` | Server port |
| `DEBUG` | ❌ | `false` | Enable debug mode |
| `NEXT_PUBLIC_API_URL` | ✅ | - | Backend URL for frontend |

---

## 🎓 Skills Demonstrated

This project showcases proficiency in:

### Backend Development
- ✅ Building RESTful APIs with FastAPI
- ✅ Async/await patterns with Python asyncio
- ✅ WebSocket implementation for real-time updates
- ✅ Data validation with Pydantic v2
- ✅ Redis integration for caching and persistence
- ✅ External API integration (SerpAPI, Gemini)
- ✅ Web scraping with httpx and BeautifulSoup

### Frontend Development
- ✅ Modern React with Next.js 16 App Router
- ✅ TypeScript for type safety
- ✅ State management with React hooks
- ✅ Component-based architecture
- ✅ Responsive design with Tailwind CSS
- ✅ API integration and error handling

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

## 🔮 Roadmap

- [ ] **Docker & Compose** - Containerized deployment
- [ ] **pytest Suite** - Unit and integration tests
- [ ] **GitHub Actions CI** - Automated testing
- [ ] **API Authentication** - JWT/API key auth
- [ ] **Rate Limiting** - Request throttling
- [ ] **Caching Layer** - Response caching
- [ ] **Export Features** - CSV/PDF export
- [ ] **Multi-language** - i18n support

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Backend README](app/README.md) | FastAPI server documentation |
| [Frontend README](frontend/README.md) | Next.js application documentation |

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ using FastAPI, Next.js, and Google Gemini**

⭐ Star this repo if you find it useful!

</div>
