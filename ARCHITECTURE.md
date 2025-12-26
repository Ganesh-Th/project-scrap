# AI Review Intelligence System - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                    (Next.js Frontend)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   REST API   │  │  WebSockets  │  │   Business   │     │
│  │  Endpoints   │  │  (optional)  │  │    Logic     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────┬────────────────────────┬────────────────┬─────────┘
          │                        │                │
          ▼                        ▼                ▼
┌──────────────────┐    ┌──────────────────┐   ┌──────────────┐
│   PostgreSQL     │    │  Redis (Broker)  │   │   Celery     │
│    Database      │    │  + Result Store  │   │   Workers    │
└──────────────────┘    └──────────────────┘   └──────┬───────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │  AI Services    │
                                              │  - Sentiment    │
                                              │  - Classifier   │
                                              │  - Clustering   │
                                              └─────────────────┘
```

## Data Flow

### 1. Job Creation Flow

```
User → Frontend → POST /api/jobs → Backend
                                      ↓
                              Create Job Record
                                      ↓
                              Queue Celery Task
                                      ↓
                              Return Job ID
```

### 2. Review Processing Flow

```
Celery Task Start
    ↓
State: QUEUED
    ↓
State: FETCHING → SerpAPI/Mock → Fetch Reviews
    ↓
State: ANALYZING → AI Services → Sentiment + Classification
    ↓
Store Reviews in DB
    ↓
State: CLUSTERING → Clustering Service → Group Reviews
    ↓
Generate Themes
    ↓
Convert to Tasks (RICE)
    ↓
State: DONE
```

### 3. Results Retrieval Flow

```
User → Frontend → GET /api/jobs/{id}/results → Backend
                                                   ↓
                                          Query Job + Reviews
                                                   ↓
                                            Query Themes + Tasks
                                                   ↓
                                          Return Complete Results
```

## Component Responsibilities

### Frontend (Next.js)
- **Job Management UI**: Create and list analysis jobs
- **Real-time Updates**: Poll for job status changes
- **Results Visualization**: Display analytics and insights
- **Task Management**: Edit RICE scores, confirm/reject tasks
- **Responsive Design**: Mobile-friendly interface

### Backend (FastAPI)
- **API Gateway**: RESTful endpoints for all operations
- **Authentication** (future): JWT-based auth
- **Job Orchestration**: Manage async job lifecycle
- **Data Validation**: Pydantic schemas
- **CORS Handling**: Allow frontend access

### Database (PostgreSQL)
- **Jobs Table**: Track analysis jobs and states
- **Reviews Table**: Store raw and analyzed reviews
- **Themes Table**: Clustered review themes
- **Tasks Table**: Generated tasks with RICE scores
- **Relationships**: Foreign keys for data integrity

### Message Queue (Redis)
- **Celery Broker**: Distribute tasks to workers
- **Result Backend**: Store task results
- **Session Storage** (future): User sessions

### Task Queue (Celery)
- **Async Processing**: Handle long-running jobs
- **Retry Logic**: Auto-retry failed tasks
- **Task Routing**: Different queues for different priorities
- **Monitoring**: Track task progress

### AI Services

#### Sentiment Analyzer
- Model: DistilBERT (fine-tuned for sentiment)
- Fallback: Rule-based analysis
- Output: sentiment (positive/negative/neutral) + confidence score

#### Multi-Label Classifier
- Approach: Rule-based keyword matching
- Categories: bug, feature, usability, requirement, praise
- Output: Score 0.0-1.0 for each category

#### Clustering Service
- Algorithm: K-Means clustering
- Features: TF-IDF vectorization
- Output: Cluster assignments + theme summaries

#### Task Converter
- Input: Theme data
- Logic: RICE score calculation
- Output: Prioritized tasks

## Database Schema

```sql
-- Jobs
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    app_name VARCHAR NOT NULL,
    app_id VARCHAR NOT NULL,
    state VARCHAR NOT NULL,  -- JobState enum
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    error_message TEXT
);

-- Reviews
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id),
    author VARCHAR,
    rating FLOAT,
    content TEXT,
    date TIMESTAMP,
    sentiment VARCHAR,
    sentiment_score FLOAT,
    is_bug FLOAT DEFAULT 0,
    is_feature FLOAT DEFAULT 0,
    is_usability FLOAT DEFAULT 0,
    is_requirement FLOAT DEFAULT 0,
    is_praise FLOAT DEFAULT 0,
    cluster_id INTEGER
);

-- Themes
CREATE TABLE themes (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id),
    cluster_id INTEGER,
    title VARCHAR,
    description TEXT,
    review_count INTEGER,
    avg_sentiment FLOAT
);

-- Tasks
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    theme_id INTEGER REFERENCES themes(id),
    title VARCHAR,
    description TEXT,
    reach INTEGER DEFAULT 0,
    impact INTEGER DEFAULT 0,
    confidence INTEGER DEFAULT 0,
    effort INTEGER DEFAULT 1,
    rice_score FLOAT DEFAULT 0,
    confirmed INTEGER DEFAULT 0  -- 0=pending, 1=confirmed, -1=rejected
);
```

## API Endpoints

### Jobs
- `POST /api/jobs` - Create new job
- `GET /api/jobs` - List all jobs
- `GET /api/jobs/{id}` - Get job details
- `GET /api/jobs/{id}/results` - Get complete results
- `GET /api/jobs/{id}/reviews` - Get job reviews
- `GET /api/jobs/{id}/themes` - Get job themes

### Tasks
- `GET /api/tasks/{id}` - Get task details
- `PUT /api/tasks/{id}` - Update task (RICE/confirmation)

### System
- `GET /` - API info
- `GET /health` - Health check
- `GET /docs` - Swagger documentation

## State Machine

```
QUEUED ──→ FETCHING ──→ ANALYZING ──→ CLUSTERING ──→ DONE
   │                                                     ↑
   └──────────────────→ FAILED ←──────────────────────┘
```

## Scalability Considerations

### Horizontal Scaling
- Add more Celery workers for parallel processing
- Use Redis clustering for higher throughput
- Database read replicas for query scaling

### Vertical Scaling
- Increase worker resources for faster AI processing
- Larger PostgreSQL instance for more data
- More Redis memory for larger queues

### Optimization
- Cache frequent queries in Redis
- Batch review processing
- Async database operations
- CDN for frontend assets

## Security

### Current
- CORS configuration
- Input validation with Pydantic
- SQL injection prevention via ORM

### Future Enhancements
- JWT authentication
- Rate limiting
- API key management
- Encryption at rest
- HTTPS/TLS

## Monitoring & Logging

### Logs
- FastAPI access logs
- Celery task logs
- Application error logs

### Metrics (future)
- Job processing time
- API response time
- Task queue depth
- Database query performance

## Technology Choices

### Why FastAPI?
- Native async support
- Auto-generated documentation
- Type hints and validation
- High performance

### Why Celery?
- Robust task queue
- Retry mechanisms
- Wide adoption
- Good monitoring tools

### Why PostgreSQL?
- ACID compliance
- Complex queries support
- JSON support
- Reliable and mature

### Why Next.js?
- Server-side rendering
- Fast performance
- Great developer experience
- TypeScript support

### Why Redis?
- Fast in-memory operations
- Celery compatibility
- Pub/sub support
- Simple deployment
