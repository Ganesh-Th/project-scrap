# AI Review Intelligence & Prioritization System (Demo)

> A demo web application that aggregates app reviews and uses AI to transform unstructured feedback into actionable, prioritized product tasks.

## 🚀 Overview

Product teams receive thousands of reviews across app stores and platforms, but manually extracting insights and prioritizing work is slow and error-prone.

This project demonstrates an **end-to-end system** that:
- Ingests app reviews asynchronously
- Analyzes them using AI (sentiment + categorization)
- Groups similar feedback into actionable tasks
- Prioritizes tasks using product frameworks (RICE / MoSCoW)
- Visualizes insights in a dashboard
- Exports structured results

> ⚠️ **Note:** This is a **portfolio/demo project**, not a production SaaS.

## 🎯 Key Features

### Review Ingestion
- Accepts App Store & Play Store app links
- Uses third-party SERP APIs for demo review ingestion
- Filters reviews by date range
- Asynchronous background jobs with progress tracking
- Review de-duplication and update handling

### AI Analysis
- Automatic language detection
- Sentence-level sentiment analysis (Positive / Neutral / Negative / Mixed)
- Multi-label category classification:
  - Bug
  - Feature Request
  - Usability Friction
  - Requirement
  - Praise
  - Other
- Confidence scoring and keyword highlighting

### Theme Clustering & Task Generation
- Converts noisy reviews into meaningful themes
- Groups similar feedback using embeddings
- Creates one actionable task per theme
- Attaches supporting review examples and sentiment distribution

### Prioritization
- Supports RICE and MoSCoW frameworks
- AI suggests initial values
- Human-in-the-loop confirmation
- Bias normalization to avoid review-volume dominance

### Dashboard
- Overview metrics and trends
- Tasks grouped by category
- Prioritized backlog view
- Raw review drill-down with AI explanations

### Export
- CSV (tasks & priorities)
- JSON (raw + processed data)
- Optional PDF summary

## 🧱 Architecture (High Level)

Frontend (Next.js)
→ Backend API (FastAPI)
→ Async Queue (Celery + Redis)
→ PostgreSQL Database

## 🔌 Review Sources

This project uses third-party SERP APIs (e.g., SerpApi) for review ingestion **for demonstration purposes only**.

In production, these would be replaced with:
- Google Play Developer API (owned apps only)
- App Store Connect API (owned apps only)
- User-uploaded datasets
- Licensed third-party providers

## 🤖 AI Design Decisions

- Sentiment is separate from category
- Multi-label classification
- Fixed taxonomy enforcement
- Explainable AI outputs

## 🚫 Non-Goals

- Real-time syncing
- Multi-user collaboration
- Enterprise compliance guarantees
- Competitor benchmarking claims

## 🛠️ Tech Stack

- Frontend: Next.js (TypeScript)
- Backend: FastAPI (Python)
- Queue: Celery + Redis
- Database: PostgreSQL
- AI: OpenAI API / Embeddings
- Review Ingestion: Third-party SERP APIs (demo)

## 📈 What This Demonstrates

- Async system design
- AI processing pipelines
- Product prioritization frameworks
- Dashboard storytelling
- Engineering trade-off awareness

## 📎 Disclaimer

This project is for **learning and portfolio purposes only**. Any production implementation must use compliant data sources.

---

*Author note: The core value of this project is how unstructured feedback is transformed into prioritized product insights.*
