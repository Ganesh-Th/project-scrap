from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.api.jobs import router as jobs_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Review Intelligence System",
    description="Analyze app reviews with AI-powered sentiment analysis and clustering",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(jobs_router)

@app.get("/")
def root():
    return {
        "message": "AI Review Intelligence System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
