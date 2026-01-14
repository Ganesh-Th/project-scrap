# � Sentiment to Sprint

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=for-the-badge&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-5.0+-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.0-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)

**A product intelligence platform that transforms unstructured user feedback into structured, actionable product insights and sprint-ready decisions.**

[Vision](#-product-vision) • [Who Is This For](#-who-is-this-for) • [User Journey](#-user-journey) • [Features](#-features) • [Screenshots](#-screenshots) • [Get Started](#-get-started)

</div>

---

## 💡 Product Vision

> To become the default AI-powered bridge between customer sentiment and agile product execution.

---

## 🎯 The Problem

Product teams struggle to manually aggregate, analyze, and prioritize large volumes of user feedback scattered across multiple platforms:

- **Feedback Overload** — Hours spent manually reading reviews across Google Play, App Store, Reddit, and forums
- **Scattered Sources** — Reviews and discussions are fragmented across platforms with no unified view
- **Unclear Prioritization** — Difficult to identify patterns and prioritize what to fix first
- **Disconnected from Execution** — Existing solutions are qualitative, slow, or disconnected from agile development frameworks

---

## ✅ The Solution

**Sentiment to Sprint** provides an end-to-end pipeline that:

1. **Scrapes** reviews from 4+ sources concurrently
2. **Analyzes** sentiment using Google Gemini AI
3. **Categorizes** findings (bugs, features, pain points, etc.)
4. **Prioritizes** tasks using MoSCoW or Lean methodologies
5. **Generates** a sprint-ready product backlog

---

## 👥 Who Is This For?

### Primary: Product Manager
| Goals | Pain Points |
|-------|-------------|
| Prioritize roadmap effectively | Feedback overload |
| Reduce analysis time | Unclear prioritization |
| Data-driven decisions | Manual review reading |

### Secondary: Founder / Early-stage Builder
| Goals | Pain Points |
|-------|-------------|
| Validate product direction quickly | Limited resources |
| Understand user needs | Noisy feedback |
| Move fast with confidence | No dedicated PM team |

---

## 🛤 User Journey

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   STEP 1    │    │   STEP 2    │    │   STEP 3    │    │   STEP 4    │    │   STEP 5    │
│             │───▶│             │───▶│             │───▶│             │───▶│             │
│   Input     │    │   Scrape    │    │  Analyze    │    │ Prioritize  │    │   Output    │
│  Product    │    │  Reviews    │    │  Sentiment  │    │  Findings   │    │   Sprint    │
│   Info      │    │  (4+ src)   │    │   (AI)      │    │  (MoSCoW)   │    │   Backlog   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

| Step | Description |
|------|-------------|
| **1. Input** | Enter product identifiers (App Store ID, Play Store ID, country, platform) |
| **2. Scrape** | System concurrently scrapes Google Play, Apple App Store, Reddit, and Google Search |
| **3. Analyze** | AI categorizes feedback into 7 finding types with sentiment analysis |
| **4. Prioritize** | Apply MoSCoW or Lean framework with sprint constraints |
| **5. Output** | Receive sprint-ready prioritized backlog with actionable tasks |

---

## ✨ Features

### Must Have (v1) ✅
| Feature | Description |
|---------|-------------|
| **Multi-Source Scraping** | Google Play, Apple App Store, Reddit, Google Search |
| **AI Sentiment Analysis** | Google Gemini-powered categorization into 7 finding types |
| **Prioritization Frameworks** | MoSCoW and Lean methodologies with sprint planning |
| **Real-Time Progress** | WebSocket updates during analysis |

### Should Have (Planned)
| Feature | Description |
|---------|-------------|
| **Exportable Outputs** | CSV/PDF export of findings and backlog |
| **Historical Comparison** | Track sentiment changes over time |

### Could Have (Future)
| Feature | Description |
|---------|-------------|
| **Jira Integration** | Push tasks directly to Jira |
| **Team Collaboration** | Shared workspaces and comments |

### Won't Have (v1)
- Real-time continuous monitoring
- Team accounts
- Native mobile apps

---

## 📊 Analysis Categories

The AI categorizes findings into 7 actionable types:

| Type | Icon | Description |
|------|------|-------------|
| `bug` | 🐛 | Technical issues, crashes, errors |
| `feature_request` | ✨ | User-requested new features |
| `requirement` | 📋 | Must-have missing features |
| `usability_friction` | 🔧 | UX issues causing frustration |
| `pain_point` | 😤 | General user dissatisfaction |
| `positive_review` | ⭐ | Things users love |
| `ai_insight` | 🤖 | AI-discovered patterns |

> 📖 For detailed category examples and API response formats, see the [Backend Documentation](app/README.md#-analysis-output-categories)

---

## 📸 Screenshots

> *Screenshots coming soon*

| Analysis Form | Results View | Prioritization |
|---------------|--------------|----------------|
| Step 1: Configure sources | Categorized findings | Sprint-ready backlog |

---

## 🚀 Get Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Redis server
- API keys: SerpAPI, Google Gemini

### Quick Links

| Documentation | Description |
|---------------|-------------|
| 📖 [Backend Setup](app/README.md#-quick-start) | Python/FastAPI installation, API keys, Redis setup |
| 📖 [Frontend Setup](frontend/README.md#-quick-start) | Next.js installation, environment config |
| 📖 [API Documentation](app/README.md#-api-endpoints) | Endpoints, request/response formats, examples |
| 📖 [System Architecture](app/README.md#-system-architecture) | Full architecture diagram and data flow |

### Access Points

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger Docs | http://localhost:8000/docs |

---

## 🔮 Roadmap

### Infrastructure
- [ ] **Docker & Compose** — Containerized deployment
- [ ] **pytest Suite** — Unit and integration tests
- [ ] **GitHub Actions CI** — Automated testing
- [ ] **API Authentication** — JWT/API key auth
- [ ] **Rate Limiting** — Request throttling

### Product Features
- [ ] **Export Features** — CSV/PDF export (Should Have)
- [ ] **Historical Comparison** — Sentiment tracking over time (Should Have)
- [ ] **Jira Integration** — Push to Jira (Could Have)
- [ ] **Team Collaboration** — Shared workspaces (Could Have)
- [ ] **Multi-language** — i18n support

---

## 📈 Success Metrics

| Metric | Description |
|--------|-------------|
| **Time to Insight** | How quickly users go from input to actionable backlog |
| **User Completion Rate** | Percentage of users who complete the full flow |
| **Output Clarity Score** | Qualitative feedback on backlog usefulness |

---

## 📚 Technical Documentation

| Document | Description |
|----------|-------------|
| [Backend README](app/README.md) | FastAPI server, architecture, API docs, skills demonstrated |
| [Frontend README](frontend/README.md) | Next.js application, components, skills demonstrated |

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
