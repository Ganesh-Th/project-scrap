import httpx
from typing import List, Dict
from datetime import datetime

class SerpAPIService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
    
    async def fetch_reviews(self, app_id: str, num_reviews: int = 50) -> List[Dict]:
        """
        Fetch app reviews from SerpAPI (Google Play Store)
        In demo mode, returns mock data if API key is 'demo_key'
        """
        if self.api_key == "demo_key":
            # Return mock reviews for demo purposes
            return self._generate_mock_reviews(num_reviews)
        
        # Real SerpAPI implementation
        params = {
            "api_key": self.api_key,
            "engine": "google_play_product",
            "product_id": app_id,
            "all_reviews": "true",
            "num": num_reviews
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            reviews = []
            if "reviews" in data:
                for review in data["reviews"]:
                    reviews.append({
                        "author": review.get("author", "Anonymous"),
                        "rating": review.get("rating", 3),
                        "content": review.get("snippet", ""),
                        "date": review.get("date", datetime.utcnow().isoformat())
                    })
            
            return reviews
    
    def _generate_mock_reviews(self, num_reviews: int) -> List[Dict]:
        """Generate mock reviews for demo purposes"""
        from datetime import timedelta
        
        mock_reviews_templates = [
            {"rating": 5, "content": "Amazing app! The new dark mode feature is exactly what I needed. Love it!", "sentiment": "positive"},
            {"rating": 1, "content": "App crashes every time I try to upload a photo. Please fix this bug!", "sentiment": "negative"},
            {"rating": 4, "content": "Great app but could use better navigation. Sometimes hard to find settings.", "sentiment": "positive"},
            {"rating": 2, "content": "Too many ads and the interface is confusing. Needs better UX design.", "sentiment": "negative"},
            {"rating": 5, "content": "Excellent! Would love to see a widget feature added in future updates.", "sentiment": "positive"},
            {"rating": 1, "content": "Login doesn't work. Gets stuck on loading screen. Very frustrating.", "sentiment": "negative"},
            {"rating": 4, "content": "Good app overall. The search function could be faster though.", "sentiment": "positive"},
            {"rating": 3, "content": "It's okay. Does what it's supposed to do but nothing special.", "sentiment": "neutral"},
            {"rating": 5, "content": "Perfect! The offline mode is a game changer. Highly recommend!", "sentiment": "positive"},
            {"rating": 1, "content": "Terrible update. The new version removed my favorite features.", "sentiment": "negative"},
            {"rating": 4, "content": "Really like it but needs better sync across devices.", "sentiment": "positive"},
            {"rating": 2, "content": "Battery drain is horrible. App uses too much power in background.", "sentiment": "negative"},
            {"rating": 5, "content": "Best app in this category. Clean interface and fast performance.", "sentiment": "positive"},
            {"rating": 1, "content": "Constant errors when trying to save data. Lost my work multiple times.", "sentiment": "negative"},
            {"rating": 4, "content": "Very useful app. Would be great to have export to PDF feature.", "sentiment": "positive"},
            {"rating": 3, "content": "Average app. Nothing wrong but nothing impressive either.", "sentiment": "neutral"},
            {"rating": 5, "content": "Absolutely love the new update! Everything works smoothly.", "sentiment": "positive"},
            {"rating": 2, "content": "UI is outdated and clunky. Needs a modern redesign.", "sentiment": "negative"},
            {"rating": 4, "content": "Great functionality but notifications are too frequent and annoying.", "sentiment": "positive"},
            {"rating": 1, "content": "App freezes constantly. Can't complete any task without it crashing.", "sentiment": "negative"},
        ]
        
        reviews = []
        base_time = datetime.utcnow()
        
        for i in range(min(num_reviews, len(mock_reviews_templates) * 3)):
            template = mock_reviews_templates[i % len(mock_reviews_templates)]
            # Generate varied timestamps (reviews from last 30 days)
            days_ago = (i * 1.5) % 30  # Spread reviews over 30 days
            review_time = base_time - timedelta(days=days_ago, hours=(i * 3) % 24)
            
            reviews.append({
                "author": f"User{i+1}",
                "rating": template["rating"],
                "content": template["content"],
                "date": review_time.isoformat()
            })
        
        return reviews
