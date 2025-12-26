from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from typing import List, Dict, Tuple
import numpy as np

class ClusteringService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
    
    def cluster_reviews(self, reviews: List[Dict], n_clusters: int = 5) -> Tuple[List[int], List[Dict]]:
        """
        Cluster reviews into themes
        Returns: (cluster_labels, theme_summaries)
        """
        if not reviews or len(reviews) == 0:
            return [], []
        
        # Extract review texts
        texts = [r.get("content", "") for r in reviews if r.get("content")]
        
        if len(texts) < n_clusters:
            n_clusters = max(1, len(texts) // 2)
        
        if len(texts) < 2:
            # Not enough reviews to cluster
            return [0] * len(reviews), []
        
        try:
            # Vectorize texts
            X = self.vectorizer.fit_transform(texts)
            
            # Perform clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X)
            
            # Generate theme summaries
            themes = self._generate_themes(reviews, cluster_labels, n_clusters)
            
            return cluster_labels.tolist(), themes
        
        except Exception as e:
            # Fallback: assign all to one cluster
            return [0] * len(reviews), []
    
    def _generate_themes(self, reviews: List[Dict], labels: np.ndarray, n_clusters: int) -> List[Dict]:
        """Generate theme summaries from clusters"""
        themes = []
        
        for cluster_id in range(n_clusters):
            # Get reviews in this cluster
            cluster_reviews = [r for i, r in enumerate(reviews) if labels[i] == cluster_id]
            
            if not cluster_reviews:
                continue
            
            # Calculate average sentiment
            sentiments = [r.get("sentiment_score", 0.5) for r in cluster_reviews]
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.5
            
            # Extract common themes from content
            theme_title = self._extract_theme_title(cluster_reviews)
            theme_desc = self._extract_theme_description(cluster_reviews)
            
            themes.append({
                "cluster_id": cluster_id,
                "title": theme_title,
                "description": theme_desc,
                "review_count": len(cluster_reviews),
                "avg_sentiment": avg_sentiment
            })
        
        return themes
    
    def _extract_theme_title(self, reviews: List[Dict]) -> str:
        """Extract a title for the theme based on common words"""
        # Simple approach: find most common significant words
        all_words = []
        for review in reviews:
            content = review.get("content", "").lower()
            words = content.split()
            # Filter common words
            significant_words = [w for w in words if len(w) > 4 and w.isalpha()]
            all_words.extend(significant_words[:3])  # Take first 3 significant words
        
        if not all_words:
            return "General Feedback"
        
        # Count word frequency
        word_freq = {}
        for word in all_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get most common word
        most_common = max(word_freq.items(), key=lambda x: x[1])[0] if word_freq else "feedback"
        
        # Determine category based on review analysis
        categories = []
        for review in reviews[:3]:  # Sample first 3 reviews
            if review.get("is_bug", 0) > 0.3:
                categories.append("Bug Reports")
            elif review.get("is_feature", 0) > 0.3:
                categories.append("Feature Requests")
            elif review.get("is_usability", 0) > 0.3:
                categories.append("Usability Issues")
            elif review.get("is_praise", 0) > 0.3:
                categories.append("User Praise")
        
        if categories:
            return max(set(categories), key=categories.count)
        
        return f"Theme: {most_common.title()}"
    
    def _extract_theme_description(self, reviews: List[Dict]) -> str:
        """Generate a description for the theme"""
        # Take first review as representative
        if reviews:
            first_review = reviews[0].get("content", "")
            return first_review[:200] + ("..." if len(first_review) > 200 else "")
        return "No description available"

class ThemeToTaskConverter:
    """Convert themes into actionable tasks with RICE scoring"""
    
    def convert_theme_to_task(self, theme: Dict) -> Dict:
        """Convert a theme into a task with initial RICE scores"""
        # Estimate RICE based on theme characteristics
        reach = theme.get("review_count", 1) * 10  # More reviews = more users affected
        
        # Impact based on sentiment and category
        avg_sentiment = theme.get("avg_sentiment", 0.5)
        impact = 3  # Default medium impact
        if avg_sentiment < 0.3:
            impact = 5  # High impact for negative sentiment
        elif avg_sentiment > 0.7:
            impact = 2  # Lower impact for already positive
        
        # Confidence - default medium
        confidence = 80  # 80% confidence
        
        # Effort - estimate based on complexity (simplified)
        effort = 5  # Default medium effort in person-weeks
        
        # Calculate RICE score: (Reach × Impact × Confidence) / Effort
        rice_score = (reach * impact * confidence) / (100 * effort)
        
        title = theme.get("title", "Untitled Task")
        description = f"Address feedback theme: {theme.get('description', '')}\n\n"
        description += f"Based on {theme.get('review_count', 0)} user reviews with average sentiment: {avg_sentiment:.2f}"
        
        return {
            "title": title,
            "description": description,
            "reach": reach,
            "impact": impact,
            "confidence": confidence,
            "effort": effort,
            "rice_score": rice_score
        }
