# Frontend - Sentiment to Sprint UI

A modern Next.js application providing a user-friendly interface for the Sentiment to Sprint API.

> 📖 For product overview and vision, see the [Main README](../README.md)

## ✨ Features

- **Two-Step Analysis Flow**: Scrape reviews → Prioritize findings
- **Real-Time Progress**: Live progress updates during scraping
- **Interactive Results**: Expandable categories with detailed findings
- **Prioritization**: MoSCoW and Lean methodologies
- **Modern UI**: Built with shadcn/ui components and Tailwind CSS
- **TypeScript**: Full type safety throughout the codebase

---

## 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| **Next.js 16** | React framework with App Router |
| **TypeScript** | Type-safe JavaScript |
| **Tailwind CSS v4** | Utility-first styling |
| **shadcn/ui** | Accessible component library |
| **React Hooks** | State management |
| **Vercel** | Frontend deployment |

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ (recommended: 20+)
- npm or yarn
- Backend API running on http://localhost:8000

### Installation

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment:**
   ```bash
   # Create .env.local file
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

5. **Open in browser:**
   - http://localhost:3000

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── globals.css      # Global styles & theme
│   │   ├── layout.tsx       # Root layout
│   │   └── page.tsx         # Main page (state machine)
│   ├── components/
│   │   ├── ui/              # shadcn/ui components
│   │   ├── Header.tsx       # App header
│   │   ├── StepIndicator.tsx
│   │   ├── AnalysisForm.tsx # Step 1: Scrape form
│   │   ├── ProgressModal.tsx
│   │   ├── ResultsView.tsx  # Analysis results
│   │   ├── PrioritizationForm.tsx  # Step 2
│   │   └── PrioritizationResults.tsx
│   ├── hooks/
│   │   └── useTaskPolling.ts # Task status polling
│   ├── lib/
│   │   ├── api.ts           # API client
│   │   └── utils.ts         # Utility functions
│   └── types/
│       └── api.ts           # TypeScript interfaces
├── .env.local               # Environment variables
├── package.json
├── tailwind.config.ts
└── tsconfig.json
```

## 🎯 User Flow

### Step 1: Analysis
1. Enter product name
2. Configure sources (Google Play, Apple Store, Reddit, Google Search)
3. Click "Start Analysis"
4. View real-time progress
5. Review categorized findings

### Step 2: Prioritization
1. Select method (MoSCoW or Lean)
2. Enter sprint duration and budget
3. Define business goal
4. Click "Generate Plan"
5. View prioritized backlog

## ⚙️ Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API URL |

## 🛠️ Available Scripts

```bash
# Development
npm run dev          # Start dev server with hot reload

# Production
npm run build        # Build for production
npm run start        # Start production server

# Code Quality
npm run lint         # Run ESLint
```

## 🎨 Theming

The app uses a purple brand theme defined in `src/app/globals.css`:

- **Primary**: `#8458B3` (Purple)
- **Gradient**: Purple to Indigo

To customize colors, edit the CSS variables in `globals.css`.

## 🚀 Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Import project in Vercel
3. Set environment variable:
   - `NEXT_PUBLIC_API_URL` = Your production API URL
4. Deploy

### Other Platforms

```bash
npm run build
npm run start
```

## 🔗 Related

- [Backend Documentation](../app/README.md) - FastAPI backend
- [Main README](../README.md) - Product overview and vision

## 📝 API Integration

The frontend communicates with the backend via REST API:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/scrape` | POST | Start scraping task |
| `/api/v1/task/{id}` | GET | Get task status/result |
| `/api/v1/prioritize` | POST | Prioritize findings |

---

## 🎓 Skills Demonstrated

This frontend showcases proficiency in:

### Frontend Development
- ✅ Modern React with Next.js 16 App Router
- ✅ TypeScript for type safety
- ✅ State management with React hooks
- ✅ Component-based architecture
- ✅ Responsive design with Tailwind CSS
- ✅ API integration and error handling

### UI/UX Design
- ✅ Accessible component patterns (shadcn/ui)
- ✅ Real-time feedback with progress indicators
- ✅ Clean, intuitive user flows
- ✅ Theme customization with CSS variables

---

Built with ❤️ using Next.js, shadcn/ui, and Tailwind CSS
