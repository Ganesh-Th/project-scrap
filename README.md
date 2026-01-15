# 🔍 Sentiment to Sprint

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=for-the-badge&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-5.0+-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind-4.0-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)

**A product intelligence platform that transforms unstructured user feedback into structured, actionable product insights and sprint-ready decisions.**

[Vision](#-product-vision) • [Who Is This For](#-who-is-this-for) • [User Journey](#-user-journey) • [Features](#-features) • [Wireframe Descriptions](#-Page-by-Page-Wireframe-Descriptions) • [Get Started](#-get-started)

</div>

---

🎓 **Website:** [Sentiment-to-Sprint](https://sts-frontend-rqc7.onrender.com/)

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

| Step 1 | | Step 2 | | Step 3 | | Step 4 | | Step 5 |
|:------:|:-:|:------:|:-:|:------:|:-:|:------:|:-:|:------:|
| 📋 **Input** | ➡️ | 🔍 **Scrape** | ➡️ | 🤖 **Analyze** | ➡️ | 📊 **Prioritize** | ➡️ | 🚀 **Output** |
| Product Info | | Reviews (4+ src) | | Sentiment (AI) | | Findings (LEAN/MoSCoW) | | Sprint Backlog |

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

## 📸 Page-by-Page Wireframe Descriptions

Detailed wireframe-level descriptions for each user-facing page.

### 🏠 Landing Page

| Aspect | Details |
|--------|---------|
| **Purpose** | Communicate value proposition and drive user to start analysis |
| **UI Elements** | App logo, tagline explaining sentiment-to-roadmap flow, Primary CTA |
| **CTA** | `Start Analysis` |
| **Success Criteria** | User understands product in under 10 seconds |

---

### 📝 Product Input Page

| Aspect | Details |
|--------|---------|
| **Purpose** | Collect inputs for scraping and analysis |
| **Inputs** | Product Name (required), App Store ID (optional), Play Store ID (optional), Country (dropdown), Platform (dropdown) |
| **CTA** | `Analyze Sentiment` |
| **Success Criteria** | Validation prevents empty submissions |

<details>
<summary>📋 Input Fields</summary>

| Field | Required | Type |
|-------|----------|------|
| Product Name | ✅ Yes | Text |
| App Store Product ID | ❌ No | Text |
| Play Store Product ID | ❌ No | Text |
| Country | ❌ No | Dropdown |
| Platform | ❌ No | Dropdown (Phone, Tablet, Chromebook) |

</details>

---

### ⏳ Analysis Progress Page

| Aspect | Details |
|--------|---------|
| **Purpose** | Show real-time analysis progress |
| **UI Elements** | Progress indicator, status messages, source completion badges |
| **Success Criteria** | User confidence that system is actively working |

---

### 📊 Sentiment Results Dashboard

| Aspect | Details |
|--------|---------|
| **Purpose** | Display categorized insights from analysis |
| **Layout** | Expandable cards for each category |
| **CTA** | `Generate Prioritization` |
| **Success Criteria** | Clear categorization and actionable summaries |

<details>
<summary>📂 Category Cards</summary>

| Category | Icon | Description |
|----------|------|-------------|
| Bugs | 🐛 | Technical issues and crashes |
| Features | ✨ | User-requested enhancements |
| Requirements | 📋 | Must-have missing features |
| Usability Friction | 🔧 | UX pain points |
| Pain Points | 😤 | General dissatisfaction |
| Positives | ⭐ | What users love |
| AI Insights | 🤖 | Pattern discoveries |

</details>

---

### ⚙️ Prioritization Setup Modal

| Aspect | Details |
|--------|---------|
| **Purpose** | Collect prioritization constraints from user |
| **CTA** | `Run Prioritization` |
| **Success Criteria** | Inputs validated and submitted successfully |

<details>
<summary>📋 Configuration Options</summary>

| Field | Options |
|-------|---------|
| Framework | MoSCoW, Lean |
| Sprint Timeframe | Custom duration |
| Resource Budget | Hours/points |
| Business Goal | Text input |

</details>

---

### 🚀 Sprint Output Page

| Aspect | Details |
|--------|---------|
| **Purpose** | Present prioritized sprint-ready backlog |
| **Layout** | Items grouped by priority bucket (Must/Should/Could/Won't or High/Medium/Low) |
| **CTAs** | `Export`, `Restart Analysis` |
| **Success Criteria** | Output directly usable for sprint planning |

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

## User Acceptance Criteria (UAC)
**Sentiment Analysis:**
- Given valid inputs, system returns categorized insights

**Prioritization:**
- Given analysis data and prioritization inputs, system returns a ranked list

**UI:**
- No broken states
- Clear error handling

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

This project is for educational and portfolio purposes.

---

<div align="center">

**Built with ❤️ using FastAPI, Next.js, and Google Gemini**

⭐ Star this repo if you find it useful!

</div>
