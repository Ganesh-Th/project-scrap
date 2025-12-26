from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Job, Review, Theme, Task, JobState
from app.services.serpapi_service import SerpAPIService
from app.services.ai_service import SentimentAnalyzer, MultiLabelClassifier
from app.services.clustering_service import ClusteringService, ThemeToTaskConverter
from app.config import settings
from datetime import datetime
import asyncio

@celery_app.task(bind=True)
def process_reviews(self, job_id: int):
    """
    Main task to process app reviews through the entire pipeline
    Stages: fetching → analyzing → clustering → done
    """
    db = SessionLocal()
    
    try:
        # Get job
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return {"error": "Job not found"}
        
        # Stage 1: Fetching reviews
        job.state = JobState.FETCHING
        db.commit()
        
        serpapi = SerpAPIService(settings.serpapi_key)
        reviews_data = asyncio.run(serpapi.fetch_reviews(job.app_id, num_reviews=50))
        
        if not reviews_data:
            job.state = JobState.FAILED
            job.error_message = "No reviews fetched"
            db.commit()
            return {"error": "No reviews fetched"}
        
        # Stage 2: Analyzing reviews
        job.state = JobState.ANALYZING
        db.commit()
        
        sentiment_analyzer = SentimentAnalyzer()
        classifier = MultiLabelClassifier()
        
        analyzed_reviews = []
        for review_data in reviews_data:
            # Sentiment analysis
            sentiment_result = sentiment_analyzer.analyze(review_data.get("content", ""))
            
            # Multi-label classification
            labels = classifier.classify(review_data.get("content", ""))
            
            # Create review object
            review_date = datetime.utcnow()
            if review_data.get("date"):
                try:
                    date_str = review_data.get("date").replace('Z', '+00:00')
                    review_date = datetime.fromisoformat(date_str)
                except (ValueError, AttributeError):
                    pass  # Use default datetime.utcnow()
            
            review = Review(
                job_id=job_id,
                author=review_data.get("author"),
                rating=review_data.get("rating"),
                content=review_data.get("content"),
                date=review_date,
                sentiment=sentiment_result["sentiment"],
                sentiment_score=sentiment_result["score"],
                is_bug=labels.get("bug", 0.0),
                is_feature=labels.get("feature", 0.0),
                is_usability=labels.get("usability", 0.0),
                is_requirement=labels.get("requirement", 0.0),
                is_praise=labels.get("praise", 0.0)
            )
            db.add(review)
            analyzed_reviews.append({
                "content": review_data.get("content", ""),
                "sentiment_score": sentiment_result["score"],
                "is_bug": labels.get("bug", 0.0),
                "is_feature": labels.get("feature", 0.0),
                "is_usability": labels.get("usability", 0.0),
                "is_requirement": labels.get("requirement", 0.0),
                "is_praise": labels.get("praise", 0.0)
            })
        
        db.commit()
        
        # Stage 3: Clustering reviews
        job.state = JobState.CLUSTERING
        db.commit()
        
        clustering_service = ClusteringService()
        cluster_labels, theme_data = clustering_service.cluster_reviews(analyzed_reviews, n_clusters=5)
        
        # Update review cluster assignments
        reviews = db.query(Review).filter(Review.job_id == job_id).all()
        for i, review in enumerate(reviews):
            if i < len(cluster_labels):
                review.cluster_id = cluster_labels[i]
        
        db.commit()
        
        # Create themes and convert to tasks
        task_converter = ThemeToTaskConverter()
        
        for theme_info in theme_data:
            theme = Theme(
                job_id=job_id,
                cluster_id=theme_info["cluster_id"],
                title=theme_info["title"],
                description=theme_info["description"],
                review_count=theme_info["review_count"],
                avg_sentiment=theme_info["avg_sentiment"]
            )
            db.add(theme)
            db.flush()  # Get theme.id
            
            # Convert theme to task
            task_data = task_converter.convert_theme_to_task(theme_info)
            task = Task(
                theme_id=theme.id,
                title=task_data["title"],
                description=task_data["description"],
                reach=task_data["reach"],
                impact=task_data["impact"],
                confidence=task_data["confidence"],
                effort=task_data["effort"],
                rice_score=task_data["rice_score"]
            )
            db.add(task)
        
        db.commit()
        
        # Mark job as done
        job.state = JobState.DONE
        job.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "status": "success",
            "job_id": job_id,
            "reviews_count": len(reviews_data),
            "themes_count": len(theme_data)
        }
    
    except Exception as e:
        # Mark job as failed
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.state = JobState.FAILED
            job.error_message = str(e)
            db.commit()
        
        raise
    
    finally:
        db.close()
