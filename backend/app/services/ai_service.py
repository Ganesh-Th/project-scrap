from transformers import pipeline
import torch
from typing import Dict, List

class SentimentAnalyzer:
    def __init__(self):
        """Initialize sentiment analysis pipeline"""
        # Use -1 for CPU, or specific GPU if available and configured
        if torch.cuda.is_available():
            self.device = torch.cuda.current_device()
        else:
            self.device = -1
        
        # Use a lightweight model for sentiment analysis
        try:
            self.classifier = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=self.device
            )
        except Exception:
            # Fallback to simple rule-based if model loading fails
            self.classifier = None
    
    def analyze(self, text: str) -> Dict[str, any]:
        """
        Analyze sentiment of text
        Returns: {"sentiment": "positive/negative/neutral", "score": float}
        """
        if not text or len(text.strip()) == 0:
            return {"sentiment": "neutral", "score": 0.5}
        
        if self.classifier:
            try:
                result = self.classifier(text[:512])[0]  # Limit text length
                label = result["label"].lower()
                score = result["score"]
                
                # Map POSITIVE/NEGATIVE to our labels
                if "pos" in label:
                    sentiment = "positive"
                elif "neg" in label:
                    sentiment = "negative"
                else:
                    sentiment = "neutral"
                
                return {"sentiment": sentiment, "score": score}
            except Exception:
                pass
        
        # Fallback to simple rule-based analysis
        return self._rule_based_sentiment(text)
    
    def _rule_based_sentiment(self, text: str) -> Dict[str, any]:
        """Simple rule-based sentiment analysis as fallback"""
        text_lower = text.lower()
        
        positive_words = ["great", "amazing", "excellent", "love", "perfect", "best", "good", "nice", "wonderful"]
        negative_words = ["bad", "terrible", "horrible", "hate", "worst", "awful", "poor", "crash", "bug", "error"]
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            score = min(0.9, 0.6 + (pos_count * 0.1))
            return {"sentiment": "positive", "score": score}
        elif neg_count > pos_count:
            score = max(0.1, 0.4 - (neg_count * 0.1))
            return {"sentiment": "negative", "score": score}
        else:
            return {"sentiment": "neutral", "score": 0.5}

class MultiLabelClassifier:
    def __init__(self):
        """Initialize multi-label classifier for review categories"""
        # Using rule-based classification for reliability
        self.categories = {
            "bug": ["crash", "bug", "error", "freeze", "stuck", "broken", "doesn't work", "not working", "issue", "problem", "fail"],
            "feature": ["feature", "add", "would love", "wish", "should have", "need", "want", "suggestion", "could use"],
            "usability": ["hard to", "difficult", "confusing", "complicated", "ux", "ui", "interface", "navigation", "design", "layout"],
            "requirement": ["need", "must have", "required", "necessary", "essential", "should", "expect"],
            "praise": ["great", "amazing", "excellent", "love", "perfect", "best", "awesome", "fantastic", "wonderful", "brilliant"]
        }
    
    def classify(self, text: str) -> Dict[str, float]:
        """
        Classify text into multiple categories
        Returns scores for each category (0.0 to 1.0)
        """
        if not text:
            return {cat: 0.0 for cat in self.categories.keys()}
        
        text_lower = text.lower()
        scores = {}
        
        for category, keywords in self.categories.items():
            # Count keyword matches
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            # Normalize score (cap at 1.0)
            scores[category] = min(1.0, matches * 0.3)
        
        return scores
