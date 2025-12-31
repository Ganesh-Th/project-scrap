import asyncio
import os
import time
import json
from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import google.generativeai as genai
from json_toon import json_to_toon

# API Keys
SERPAPI_KEY = os.getenv('SERPAPI_KEY')
if not SERPAPI_KEY:
    raise RuntimeError("SERPAPI_KEY not set")

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set")

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Country mapping based on https://serpapi.com/apple-regions
# Maps both country codes and country names (case-insensitive) to country codes
COUNTRY_MAPPING = {
    # Country codes
    "us": "us", "gb": "gb", "ca": "ca", "au": "au", "de": "de", "fr": "fr", "it": "it", "es": "es",
    "jp": "jp", "cn": "cn", "in": "in", "br": "br", "mx": "mx", "ru": "ru", "kr": "kr", "nl": "nl",
    "se": "se", "no": "no", "dk": "dk", "fi": "fi", "pl": "pl", "cz": "cz", "at": "at", "ch": "ch",
    "be": "be", "ie": "ie", "nz": "nz", "sg": "sg", "hk": "hk", "tw": "tw", "th": "th", "ph": "ph",
    "id": "id", "my": "my", "vn": "vn", "ae": "ae", "sa": "sa", "il": "il", "tr": "tr", "za": "za",
    "eg": "eg", "ng": "ng", "ke": "ke", "ar": "ar", "cl": "cl", "co": "co", "pe": "pe", "ve": "ve",
    "ua": "ua", "ro": "ro", "hu": "hu", "gr": "gr", "pt": "pt", "bg": "bg", "hr": "hr", "sk": "sk",
    "si": "si", "ee": "ee", "lv": "lv", "lt": "lt", "is": "is", "lu": "lu", "mt": "mt", "cy": "cy",
    # Country names (will be converted to lowercase for matching)
    "united states": "us", "usa": "us", "america": "us",
    "united kingdom": "gb", "uk": "gb", "britain": "gb", "england": "gb",
    "canada": "ca",
    "australia": "au",
    "germany": "de",
    "france": "fr",
    "italy": "it",
    "spain": "es",
    "japan": "jp",
    "china": "cn",
    "india": "in",
    "brazil": "br",
    "mexico": "mx",
    "russia": "ru",
    "south korea": "kr", "korea": "kr",
    "netherlands": "nl", "holland": "nl",
    "sweden": "se",
    "norway": "no",
    "denmark": "dk",
    "finland": "fi",
    "poland": "pl",
    "czech republic": "cz", "czechia": "cz",
    "austria": "at",
    "switzerland": "ch",
    "belgium": "be",
    "ireland": "ie",
    "new zealand": "nz",
    "singapore": "sg",
    "hong kong": "hk",
    "taiwan": "tw",
    "thailand": "th",
    "philippines": "ph",
    "indonesia": "id",
    "malaysia": "my",
    "vietnam": "vn",
    "united arab emirates": "ae", "uae": "ae",
    "saudi arabia": "sa",
    "israel": "il",
    "turkey": "tr",
    "south africa": "za",
    "egypt": "eg",
    "nigeria": "ng",
    "kenya": "ke",
    "argentina": "ar",
    "chile": "cl",
    "colombia": "co",
    "peru": "pe",
    "venezuela": "ve",
    "ukraine": "ua",
    "romania": "ro",
    "hungary": "hu",
    "greece": "gr",
    "portugal": "pt",
    "bulgaria": "bg",
    "croatia": "hr",
    "slovakia": "sk",
    "slovenia": "si",
    "estonia": "ee",
    "latvia": "lv",
    "lithuania": "lt",
    "iceland": "is",
    "luxembourg": "lu",
    "malta": "mt",
    "cyprus": "cy"
}

def get_country_code(user_input: str) -> str:
    """Convert user input (country name or code) to valid country code."""
    if not user_input:
        return "us"  # Default
    
    user_input = user_input.strip().lower()
    
    # Direct code match
    if user_input in COUNTRY_MAPPING:
        return COUNTRY_MAPPING[user_input]
    
    # Try to find by partial match in country names
    for key, code in COUNTRY_MAPPING.items():
        if user_input in key or key in user_input:
            return code
    
    # If no match found, return the input as-is (might be a valid code we don't have mapped)
    print(f"Warning: '{user_input}' not found in mapping. Using as-is.")
    return user_input


# ============================================================================
# Task 1: Google Play Store Reviews Scraper
# ============================================================================
async def scrape_google_play_reviews(product_id: str, platform: str) -> dict:
    """
    Scrape Google Play Store reviews.
    
    Args:
        product_id: Google Play Store product ID (e.g., com.google.android.youtube)
        platform: Platform type (phone/tablet/tv/wearables/auto/chromebook)
    
    Returns:
        Dictionary containing reviews data
    """
    print(f"\n[Google Play Store] Starting scrape for product: {product_id}, platform: {platform}")
    
    params = {
        "engine": "google_play_product",
        "store": "apps",
        "product_id": product_id,
        "all_reviews": "true",
        "platform": platform,
        "sort_by": "2",
        "num": "199",
        "json_restrictor": "reviews[].{id, rating, snippet, likes, iso_date}",
        "api_key": SERPAPI_KEY
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        reviews = results.get("reviews", [])
        
        print(f"[Google Play Store] Successfully fetched {len(reviews)} reviews")
        
        # Commented out JSON file saving
        # with open("Google_reviews.json", "w", encoding="utf-8") as f:
        #     json.dump(reviews, f, ensure_ascii=False, indent=2)
        # print("Saved reviews to Google_reviews.json")
        
        return {
            "source": "google_play_store",
            "product_id": product_id,
            "platform": platform,
            "reviews": reviews,
            "total_reviews": len(reviews)
        }
    except Exception as e:
        print(f"[Google Play Store] Error: {e}")
        return {
            "source": "google_play_store",
            "product_id": product_id,
            "platform": platform,
            "reviews": [],
            "total_reviews": 0,
            "error": str(e)
        }


# ============================================================================
# Task 2: Apple App Store Reviews Scraper
# ============================================================================
async def scrape_apple_store_reviews(product_id: str, country: str, target_reviews: int = 199) -> dict:
    """
    Scrape Apple App Store reviews.
    
    Args:
        product_id: Apple App Store product ID (e.g., 544007664)
        country: Country code (e.g., us, gb, ca)
        target_reviews: Target number of reviews to fetch (default: 199)
    
    Returns:
        Dictionary containing reviews data
    """
    print(f"\n[Apple App Store] Starting scrape for product: {product_id}, country: {country}")
    
    all_reviews = []
    page = 1
    
    try:
        while len(all_reviews) < target_reviews:
            params = {
                "engine": "apple_reviews",
                "product_id": product_id,
                "country": country,
                "page": page,
                "json_restrictor": "reviews[].{id, title, text, rating, review_date, reviewed_version}, serpapi_pagination",
                "api_key": SERPAPI_KEY
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            reviews = results.get("reviews", [])
            if not reviews:
                break
            
            all_reviews.extend(reviews)
            print(f"[Apple App Store] Fetched page {page}... Total reviews so far: {len(all_reviews)}")
            
            serpapi_pagination = results.get("serpapi_pagination", {})
            if "next" not in serpapi_pagination:
                break
            
            page += 1
        
        all_reviews = all_reviews[:target_reviews]
        
        print(f"[Apple App Store] Successfully fetched {len(all_reviews)} reviews")
        
        # Commented out JSON file saving
        # with open("apple_reviews.json", "w", encoding="utf-8") as f:
        #     json.dump(all_reviews, f, ensure_ascii=False, indent=2)
        # print(f"Successfully saved {len(all_reviews)} reviews to apple_reviews.json")
        
        return {
            "source": "apple_app_store",
            "product_id": product_id,
            "country": country,
            "reviews": all_reviews,
            "total_reviews": len(all_reviews)
        }
    except Exception as e:
        print(f"[Apple App Store] Error: {e}")
        return {
            "source": "apple_app_store",
            "product_id": product_id,
            "country": country,
            "reviews": [],
            "total_reviews": 0,
            "error": str(e)
        }


# ============================================================================
# Task 3: Reddit Scraper
# ============================================================================
async def scrape_reddit(topic: str, keywords: list) -> dict:
    """
    Scrape Reddit subreddit for topics and discussions.
    
    Args:
        topic: Subreddit name (e.g., Python, Gaming, Tech)
        keywords: List of keywords to filter for
    
    Returns:
        Dictionary containing scraped Reddit data
    """
    print(f"\n[Reddit] Starting scrape for topic: {topic}, keywords: {keywords}")
    
    base_reddit_url = "https://www.reddit.com"
    subreddits = [
        f"https://www.reddit.com/r/{topic}",
        f"https://www.reddit.com/r/{topic}/hot"
    ]
    
    all_data = []
    
    for url in subreddits:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        subreddit_name = url.split("/")[-1]
        print(f'[Reddit] Scraping for: {subreddit_name}')
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            
            subreddit_data = {
                "subreddit_name": subreddit_name,
                "url": url,
                "title": soup.title.string if (soup.title and soup.title.string) else "No title",
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            topics = []
            for heading in soup.find_all(["h1", "h2", "h3", "h4"]):
                text = heading.get_text(strip=True)
                
                if text and len(text) > 3:
                    if any(k in text.lower() for k in keywords):
                        topics.append({
                            "title": text,
                            "type": f"{topic}_topic"
                        })
            
            discussions = []
            seen_urls = set()
            
            for link in soup.find_all("a", href=True):
                text = link.get_text(strip=True)
                href = link["href"]
                
                if text and len(text) > 1 and "/comments/" in href and href not in seen_urls:
                    seen_urls.add(href)
                    full_url = urljoin(base_reddit_url, href)
                    
                    discussions.append({
                        "title": text[:100] + " ... " if len(text) > 100 else text,
                        "url": full_url,
                        "type": "discussion"
                    })
            
            subreddit_data["found_topics"] = topics
            subreddit_data["discussions"] = discussions
            
            all_data.append(subreddit_data)
            await asyncio.sleep(2)  # Use asyncio.sleep instead of time.sleep for async
        
        except Exception as e:
            print(f'[Reddit] Error: {e}')
    
    total_topics = sum(len(subreddit.get("found_topics", [])) for subreddit in all_data)
    total_discussions = sum(len(subreddit.get("discussions", [])) for subreddit in all_data)
    
    print(f"[Reddit] Successfully scraped {total_topics} topics, {total_discussions} discussions")
    
    # Commented out JSON file saving
    # with open("reddit.json", "w", encoding="utf-8") as file:
    #     json.dump(all_data, file, indent=2, ensure_ascii=True)
    # print(f'reddit.json is saved')
    
    return {
        "source": "reddit",
        "topic": topic,
        "keywords": keywords,
        "data": all_data,
        "total_topics": total_topics,
        "total_discussions": total_discussions
    }


# ============================================================================
# Helper Function: Convert JSON to TOON Format
# ============================================================================
def convert_json_to_toon(valid_results: list) -> tuple[str, dict]:
    """
    Convert JSON review data to TOON format for efficient AI processing.
    TOON format reduces token usage by 30-60% compared to JSON.
    
    Args:
        valid_results: List of dictionaries containing scraped data from all sources
    
    Returns:
        Tuple of (toon_text: str, data_summary: dict)
    """
    if not valid_results:
        return "", {}
    
    try:
        # Convert entire valid_results to TOON format
        toon_text = json_to_toon(valid_results)
        
        # Build data_summary for tracking
        data_summary = {}
        for data in valid_results:
            source = data.get("source", "unknown")
            
            if source == "google_play_store":
                reviews = data.get("reviews", [])
                data_summary[source] = {
                    "total_reviews": len(reviews),
                    "analyzed_reviews": len(reviews)
                }
            elif source == "apple_app_store":
                reviews = data.get("reviews", [])
                data_summary[source] = {
                    "total_reviews": len(reviews),
                    "analyzed_reviews": len(reviews)
                }
            elif source == "reddit":
                data_summary[source] = {
                    "total_topics": data.get("total_topics", 0),
                    "total_discussions": data.get("total_discussions", 0),
                    "analyzed_items": data.get("total_topics", 0) + data.get("total_discussions", 0)
                }
        
        return toon_text, data_summary
    except Exception as e:
        print(f"[TOON] Error converting to TOON format: {e}")
        # Fallback: return empty string and let caller handle
        return "", {}


# ============================================================================
# Task 4: Gemini API Sentiment Analysis
# ============================================================================
async def analyze_sentiment_with_gemini(all_results: list) -> dict:
    """
    Analyze sentiment of combined scraped data from all sources using Gemini API.
    Focuses on identifying pain points and actionable insights for app developers.
    
    Args:
        all_results: List of dictionaries containing scraped data from all sources
    
    Returns:
        Dictionary containing combined sentiment analysis results with pain points
    """
    print(f"\n[Gemini] Starting combined sentiment analysis for {len(all_results)} source(s)")
    
    try:
        # Use gemini-1.5-pro or gemini-pro based on availability
        try:
            model = genai.GenerativeModel('gemini-1.5-pro')
        except:
            model = genai.GenerativeModel('gemini-pro')
        
        # Filter out results with errors
        valid_results = [r for r in all_results if r and not r.get("error")]
        
        if not valid_results:
            return {
                "error": "No valid data to analyze",
                "sources": []
            }
        
        # Convert JSON to TOON format (30-60% more token-efficient than JSON)
        toon_text, data_summary = convert_json_to_toon(valid_results)
        
        if not toon_text:
            return {
                "error": "No text data to analyze from any source",
                "sources": [r.get("source") for r in valid_results]
            }
        
        # Use TOON text directly (already formatted efficiently)
        combined_text = toon_text
        
        # Estimate token count (rough: 1 token ≈ 4 characters)
        estimated_tokens = len(combined_text) // 4
        print(f"[Gemini] Estimated input tokens: ~{estimated_tokens}")
        
        # If data is too large, use batch processing or summarization
        MAX_TOKENS_PER_REQUEST = 1000000  # Gemini 1.5 Pro supports up to 2M tokens, but we'll be conservative
        
        if estimated_tokens > MAX_TOKENS_PER_REQUEST:
            print(f"[Gemini] Large dataset detected. Using batch processing...")
            return await _analyze_sentiment_batch_processing(model, valid_results, toon_text, data_summary)
        
        prompt = f"""You are an expert app analyst. Analyze the following user reviews and discussions from multiple sources (Google Play Store, Apple App Store, and/or Reddit) to identify pain points and provide actionable insights for app developers.

The data is provided in TOON (Token-Oriented Object Notation) format, which is a compact, token-efficient format. Parse the TOON structure to extract all reviews and discussions.

CRITICAL: You must respond with VALID JSON only. No markdown, no code blocks, just pure JSON.

Analyze ALL the reviews and provide a comprehensive analysis in the following JSON structure:

{{
  "overall_sentiment": {{
    "positive_percentage": <number>,
    "negative_percentage": <number>,
    "neutral_percentage": <number>,
    "average_rating": <number>,
    "total_reviews_analyzed": <number>
  }},
  "pain_points": [
    {{
      "category": "<bug|performance|ux|feature_request|pricing|content|other>",
      "issue": "<specific problem description>",
      "frequency": <number of times mentioned>,
      "severity": "<high|medium|low>",
      "sample_reviews": ["<review text 1>", "<review text 2>", "<review text 3>"],
      "recommendation": "<specific actionable step to fix this issue>",
      "priority_score": <number 1-10, higher = more urgent>
    }}
  ],
  "positive_feedback": [
    {{
      "theme": "<what users love>",
      "frequency": <number>,
      "sample_reviews": ["<review text 1>", "<review text 2>"]
    }}
  ],
  "source_comparison": {{
    "google_play_store": {{
      "sentiment_breakdown": {{"positive": <number>, "negative": <number>, "neutral": <number>}},
      "top_issues": ["<issue 1>", "<issue 2>", "<issue 3>"]
    }},
    "apple_app_store": {{
      "sentiment_breakdown": {{"positive": <number>, "negative": <number>, "neutral": <number>}},
      "top_issues": ["<issue 1>", "<issue 2>", "<issue 3>"]
    }},
    "reddit": {{
      "sentiment_breakdown": {{"positive": <number>, "negative": <number>, "neutral": <number>}},
      "top_issues": ["<issue 1>", "<issue 2>", "<issue 3>"]
    }}
  }},
  "priority_actions": [
    {{
      "action": "<specific action to take>",
      "reason": "<why this is important>",
      "expected_impact": "<high|medium|low>",
      "effort_required": "<high|medium|low>"
    }}
  ],
  "key_insights": [
    "<insight 1>",
    "<insight 2>",
    "<insight 3>"
  ]
}}

INSTRUCTIONS:
1. Analyze EVERY review provided (not just samples)
2. Identify ALL pain points mentioned, categorize them, and count frequency
3. Prioritize pain points by frequency and severity (high severity = crashes, data loss, security issues)
4. Provide SPECIFIC, ACTIONABLE recommendations for each pain point
5. Identify what users love (positive feedback) to maintain/improve
6. Compare sentiment across different sources
7. Rank priority actions by impact vs effort (quick wins first)

DATA FROM ALL SOURCES (in TOON format):
{combined_text}

Remember: Respond with VALID JSON only. No markdown formatting, no code blocks."""
        
        # Run async call to Gemini
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: model.generate_content(prompt)
        )
        
        analysis_text = response.text.strip()
        
        # Try to parse JSON from response (remove markdown code blocks if present)
        try:
            # Remove markdown code blocks if present
            if analysis_text.startswith("```json"):
                analysis_text = analysis_text[7:]  # Remove ```json
            elif analysis_text.startswith("```"):
                analysis_text = analysis_text[3:]   # Remove ```
            
            if analysis_text.endswith("```"):
                analysis_text = analysis_text[:-3]  # Remove closing ```
            
            analysis_text = analysis_text.strip()
            
            # Parse JSON
            analysis_json = json.loads(analysis_text)
            
            sources_analyzed = [r.get("source") for r in valid_results]
            print(f"[Gemini] Combined sentiment analysis completed for sources: {', '.join(sources_analyzed)}")
            
            return {
                "sources": sources_analyzed,
                "sentiment_analysis": analysis_json,
                "data_summary": data_summary,
                "raw_response": analysis_text  # Keep raw for debugging
            }
        except json.JSONDecodeError as e:
            print(f"[Gemini] Warning: Could not parse JSON response. Returning text format. Error: {e}")
            print(f"[Gemini] First 500 chars of response: {analysis_text[:500]}")
            # Return text format as fallback
            sources_analyzed = [r.get("source") for r in valid_results]
            return {
                "sources": sources_analyzed,
                "sentiment_analysis": {"text": analysis_text},
                "data_summary": data_summary,
                "parse_error": str(e)
            }
    
    except Exception as e:
        print(f"[Gemini] Error during sentiment analysis: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "sources": [r.get("source") for r in all_results if r and not r.get("error")]
        }


async def _analyze_sentiment_batch_processing(model, valid_results: list, toon_text: str, data_summary: dict) -> dict:
    """
    Handle large datasets by processing in batches based on token limits.
    Uses TOON format text directly (already formatted efficiently from all sources).
    
    Args:
        model: Gemini model instance
        valid_results: List of valid result dictionaries
        toon_text: TOON format text (token-efficient format)
        data_summary: Dictionary with data summary
    
    Returns:
        Dictionary containing aggregated sentiment analysis results
    """
    print(f"[Gemini] Processing large dataset in batches (using TOON format from all sources)...")
    
    # Use TOON text directly
    combined_text = toon_text
    total_size = len(combined_text)
    print(f"[Gemini] Total TOON text size: {total_size:,} characters (~{total_size // 4:,} tokens)")
    
    # Split into chunks based on token limits
    # Rough estimate: 1 token ≈ 4 characters, target ~800k tokens per batch (conservative)
    MAX_CHARS_PER_BATCH = 3200000  # ~800k tokens
    batch_results = []
    
    # Split combined_text into chunks
    batch_num = 1
    start_idx = 0
    
    while start_idx < total_size:
        end_idx = min(start_idx + MAX_CHARS_PER_BATCH, total_size)
        batch_text = combined_text[start_idx:end_idx]
        
        # Try to split at a section boundary (double newline) to avoid cutting mid-review
        if end_idx < total_size:
            # Look for the last section separator in this chunk
            last_section_sep = batch_text.rfind("\n\n")
            if last_section_sep > MAX_CHARS_PER_BATCH * 0.8:  # Only if we're not too close to start
                batch_text = batch_text[:last_section_sep]
                end_idx = start_idx + last_section_sep + 2
        
        batch_info = f"Batch {batch_num} (characters {start_idx:,} to {end_idx:,} of {total_size:,})"
        
        prompt = f"""You are an expert app analyst. Analyze these user reviews and discussions from multiple sources to identify pain points. The data is in TOON (Token-Oriented Object Notation) format. Parse the TOON structure to extract reviews. Respond with VALID JSON only.

{{
  "pain_points": [{{"category": "<bug|performance|ux|feature_request|pricing|content|other>", "issue": "<description>", "frequency": <number>}}],
  "positive_feedback": [{{"theme": "<description>", "frequency": <number>}}],
  "sentiment_breakdown": {{"positive": <number>, "negative": <number>, "neutral": <number>}}
}}

{batch_info} (TOON format):
{batch_text}"""
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content(prompt)
            )
            response_text = response.text.strip()
            
            # Clean JSON response
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            elif response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            batch_result = json.loads(response_text)
            batch_result["batch_info"] = batch_info
            batch_result["chars_processed"] = len(batch_text)
            batch_results.append(batch_result)
            print(f"[Gemini] Processed batch {batch_num} ({len(batch_text):,} characters)")
            
            # Move to next batch
            start_idx = end_idx
            batch_num += 1
        except Exception as e:
            print(f"[Gemini] Error processing batch {batch_num}: {e}")
            import traceback
            traceback.print_exc()
            # Skip this batch and continue
            start_idx = end_idx
            batch_num += 1
    
    # Aggregate batch results intelligently
    aggregated = _aggregate_batch_results(batch_results, valid_results, data_summary)
    
    return aggregated


def _aggregate_batch_results(batch_results: list, valid_results: list, data_summary: dict) -> dict:
    """
    Aggregate results from multiple batches into a unified analysis.
    
    Args:
        batch_results: List of batch analysis results
        valid_results: Original valid results
        data_summary: Data summary dictionary
    
    Returns:
        Aggregated sentiment analysis dictionary
    """
    # Aggregate pain points (merge by issue, sum frequencies)
    pain_points_map = {}
    for batch in batch_results:
        for pp in batch.get("pain_points", []):
            issue = pp.get("issue", "").lower().strip()
            if issue:
                if issue not in pain_points_map:
                    pain_points_map[issue] = {
                        "category": pp.get("category", "other"),
                        "issue": pp.get("issue", ""),
                        "frequency": 0,
                        "severity": pp.get("severity", "medium"),
                        "sample_reviews": [],
                        "priority_score": 0
                    }
                pain_points_map[issue]["frequency"] += pp.get("frequency", 1)
                # Keep first 3 sample reviews
                if len(pain_points_map[issue]["sample_reviews"]) < 3:
                    pain_points_map[issue]["sample_reviews"].extend(pp.get("sample_reviews", [])[:3])
    
    # Convert to list and calculate priority scores
    pain_points = []
    for pp in pain_points_map.values():
        # Priority = frequency * severity_multiplier
        severity_mult = {"high": 3, "medium": 2, "low": 1}.get(pp["severity"], 1)
        pp["priority_score"] = min(10, pp["frequency"] * severity_mult // 5)
        pain_points.append(pp)
    
    # Sort by priority
    pain_points.sort(key=lambda x: x["priority_score"], reverse=True)
    
    # Aggregate positive feedback
    positive_feedback_map = {}
    for batch in batch_results:
        for pf in batch.get("positive_feedback", []):
            theme = pf.get("theme", "").lower().strip()
            if theme:
                if theme not in positive_feedback_map:
                    positive_feedback_map[theme] = {
                        "theme": pf.get("theme", ""),
                        "frequency": 0,
                        "sample_reviews": []
                    }
                positive_feedback_map[theme]["frequency"] += pf.get("frequency", 1)
                if len(positive_feedback_map[theme]["sample_reviews"]) < 3:
                    positive_feedback_map[theme]["sample_reviews"].extend(pf.get("sample_reviews", [])[:3])
    
    positive_feedback = sorted(positive_feedback_map.values(), key=lambda x: x["frequency"], reverse=True)
    
    # Aggregate sentiment breakdown
    total_positive = sum(b.get("sentiment_breakdown", {}).get("positive", 0) for b in batch_results)
    total_negative = sum(b.get("sentiment_breakdown", {}).get("negative", 0) for b in batch_results)
    total_neutral = sum(b.get("sentiment_breakdown", {}).get("neutral", 0) for b in batch_results)
    total_sentiment = total_positive + total_negative + total_neutral
    
    if total_sentiment > 0:
        positive_pct = (total_positive / total_sentiment) * 100
        negative_pct = (total_negative / total_sentiment) * 100
        neutral_pct = (total_neutral / total_sentiment) * 100
    else:
        positive_pct = negative_pct = neutral_pct = 0
    
    # Calculate average rating from reviews with ratings
    ratings = []
    for data in valid_results:
        if data.get("source") == "google_play_store":
            for r in data.get("reviews", []):
                rating = r.get("rating")
                if rating:
                    ratings.append(float(rating))
        elif data.get("source") == "apple_app_store":
            for r in data.get("reviews", []):
                rating = r.get("rating")
                if rating:
                    ratings.append(float(rating))
    
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    # Calculate total reviews analyzed from data_summary
    total_reviews = 0
    for source, stats in data_summary.items():
        if "analyzed_reviews" in stats:
            total_reviews += stats.get("analyzed_reviews", 0)
        elif "analyzed_items" in stats:
            total_reviews += stats.get("analyzed_items", 0)
    
    # Build aggregated result
    aggregated_analysis = {
        "overall_sentiment": {
            "positive_percentage": round(positive_pct, 1),
            "negative_percentage": round(negative_pct, 1),
            "neutral_percentage": round(neutral_pct, 1),
            "average_rating": round(avg_rating, 2),
            "total_reviews_analyzed": total_reviews
        },
        "pain_points": pain_points[:20],  # Top 20
        "positive_feedback": positive_feedback[:10],  # Top 10
        "source_comparison": {
            # Can be enhanced to track per-source breakdown
        },
        "priority_actions": [
            {
                "action": f"Fix: {pp['issue']}",
                "reason": f"High frequency ({pp['frequency']} mentions) and {pp['severity']} severity",
                "expected_impact": "high" if pp["severity"] == "high" else "medium",
                "effort_required": "medium"
            }
            for pp in pain_points[:5]
        ],
        "key_insights": [
            f"Top pain point: {pain_points[0]['issue']} ({pain_points[0]['frequency']} mentions)" if pain_points else "No major pain points identified",
            f"Most loved feature: {positive_feedback[0]['theme']} ({positive_feedback[0]['frequency']} mentions)" if positive_feedback else "Limited positive feedback",
            f"Overall sentiment: {round(positive_pct, 1)}% positive, {round(negative_pct, 1)}% negative"
        ]
    }
    
    return {
        "sources": [r.get("source") for r in valid_results],
        "sentiment_analysis": aggregated_analysis,
        "data_summary": data_summary,
        "note": f"Results processed in {len(batch_results)} batches (combined all sources)"
    }


# ============================================================================
# Main Execution Function
# ============================================================================
async def main():
    """Main function to collect user inputs and execute scrapers conditionally."""
    
    print("=" * 60)
    print("Multi-Source Scraper with Sentiment Analysis")
    print("=" * 60)
    
    # Collect all user inputs
    print("\n--- Google Play Store Inputs ---")
    google_product_id = input("Enter Google Play Store product ID (press Enter to skip): ").strip()
    google_platform = ""
    if google_product_id:
        google_platform = input("Enter platform (phone/tablet/tv/wearables/auto/chromebook): ").strip().lower()
        if not google_platform:
            google_platform = "phone"
            print(f"Using default platform: {google_platform}")
    
    print("\n--- Apple App Store Inputs ---")
    apple_product_id = input("Enter Apple App Store product ID (press Enter to skip): ").strip()
    apple_country = ""
    if apple_product_id:
        country_input = input("Enter country (code like 'us' or name like 'United States'): ").strip()
        apple_country = get_country_code(country_input)
        print(f"Using country code: {apple_country}")
    
    print("\n--- Reddit Inputs ---")
    reddit_topic = input("Enter the Subreddit name (press Enter to skip): ").strip()
    reddit_keywords = []
    if reddit_topic:
        keywords_input = input("Enter keywords to filter for, separated by commas: ").strip()
        if keywords_input:
            reddit_keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
        if not reddit_keywords:
            reddit_keywords = [reddit_topic]
    
    # Determine execution mode
    tasks_to_run = []
    run_google = bool(google_product_id)
    run_apple = bool(apple_product_id)
    run_reddit = bool(reddit_topic and reddit_keywords)
    
    # Run conditionally
    if run_google:
        tasks_to_run.append(scrape_google_play_reviews(google_product_id, google_platform))
    
    if run_apple:
        tasks_to_run.append(scrape_apple_store_reviews(apple_product_id, apple_country))
    
    if run_reddit:
        tasks_to_run.append(scrape_reddit(reddit_topic, reddit_keywords))
    
    if not tasks_to_run:
        print("\nNo valid inputs provided. Exiting.")
        return
    
    # Execute scrapers (async if multiple, sync if single)
    print(f"\n{'=' * 60}")
    print(f"Executing {len(tasks_to_run)} scraper(s)...")
    print(f"{'=' * 60}")
    
    # Wait for all scrapers to complete
    if len(tasks_to_run) > 1:
        # Run all tasks concurrently
        results = await asyncio.gather(*tasks_to_run, return_exceptions=True)
    else:
        # Run single task
        results = [await tasks_to_run[0]]
    
    # Filter out errors and collect valid results
    valid_results = []
    for result in results:
        if isinstance(result, Exception):
            print(f"Error in scraper: {result}")
            continue
        
        if result and not result.get("error"):
            valid_results.append(result)
    
    # Perform combined sentiment analysis on all results
    if valid_results:
        print(f"\n{'=' * 60}")
        print(f"All {len(valid_results)} scraper(s) completed.")
        print(f"{'=' * 60}")
        
        # Save JSON results to file for testing
        output_filename = "scraped_data.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(valid_results, f, indent=2, ensure_ascii=False)
        print(f"\nScraped data saved to {output_filename}")
        print(f"Total sources: {len(valid_results)}")
        
        # Run Gemini API sentiment analysis
        print(f"\nCombining results for sentiment analysis...")
        sentiment_result = await analyze_sentiment_with_gemini(valid_results)
        
        # Display combined results
        print(f"\n{'=' * 60}")
        print("COMBINED SENTIMENT ANALYSIS RESULTS")
        print(f"{'=' * 60}\n")
        
        if sentiment_result.get("error"):
            print(f"Error in sentiment analysis: {sentiment_result['error']}\n")
        else:
            sources = sentiment_result.get("sources", [])
            print(f"Sources analyzed: {', '.join([s.replace('_', ' ').title() for s in sources])}\n")
            
            # Display structured analysis
            analysis = sentiment_result.get("sentiment_analysis", {})
            
            if isinstance(analysis, dict) and "overall_sentiment" in analysis:
                # Structured JSON output
                print("=" * 60)
                print("OVERALL SENTIMENT")
                print("=" * 60)
                overall = analysis.get("overall_sentiment", {})
                print(f"Positive: {overall.get('positive_percentage', 0):.1f}%")
                print(f"Negative: {overall.get('negative_percentage', 0):.1f}%")
                print(f"Neutral: {overall.get('neutral_percentage', 0):.1f}%")
                print(f"Average Rating: {overall.get('average_rating', 0):.2f}/5")
                print(f"Total Reviews Analyzed: {overall.get('total_reviews_analyzed', 0)}")
                
                # Pain Points
                pain_points = analysis.get("pain_points", [])
                if pain_points:
                    print(f"\n{'=' * 60}")
                    print(f"PAIN POINTS ({len(pain_points)} identified)")
                    print("=" * 60)
                    for i, pp in enumerate(pain_points[:10], 1):  # Show top 10
                        print(f"\n{i}. [{pp.get('category', 'unknown').upper()}] {pp.get('issue', 'N/A')}")
                        print(f"   Frequency: {pp.get('frequency', 0)} mentions | Severity: {pp.get('severity', 'N/A')} | Priority: {pp.get('priority_score', 0)}/10")
                        print(f"   Recommendation: {pp.get('recommendation', 'N/A')}")
                
                # Priority Actions
                priority_actions = analysis.get("priority_actions", [])
                if priority_actions:
                    print(f"\n{'=' * 60}")
                    print("PRIORITY ACTIONS")
                    print("=" * 60)
                    for i, action in enumerate(priority_actions[:5], 1):  # Show top 5
                        print(f"\n{i}. {action.get('action', 'N/A')}")
                        print(f"   Impact: {action.get('expected_impact', 'N/A')} | Effort: {action.get('effort_required', 'N/A')}")
                        print(f"   Reason: {action.get('reason', 'N/A')}")
                
                # Positive Feedback
                positive_feedback = analysis.get("positive_feedback", [])
                if positive_feedback:
                    print(f"\n{'=' * 60}")
                    print("POSITIVE FEEDBACK")
                    print("=" * 60)
                    for i, feedback in enumerate(positive_feedback[:5], 1):  # Show top 5
                        print(f"\n{i}. {feedback.get('theme', 'N/A')} (mentioned {feedback.get('frequency', 0)} times)")
                
                # Key Insights
                insights = analysis.get("key_insights", [])
                if insights:
                    print(f"\n{'=' * 60}")
                    print("KEY INSIGHTS")
                    print("=" * 60)
                    for i, insight in enumerate(insights, 1):
                        print(f"{i}. {insight}")
                
                # Save structured analysis to file
                analysis_filename = "sentiment_analysis.json"
                with open(analysis_filename, "w", encoding="utf-8") as f:
                    json.dump(sentiment_result, f, indent=2, ensure_ascii=False)
                print(f"\n{'=' * 60}")
                print(f"Full analysis saved to {analysis_filename}")
                print("=" * 60)
            else:
                # Fallback to text display
                print("-" * 60)
                print(analysis if isinstance(analysis, str) else json.dumps(analysis, indent=2))
                print("-" * 60)
            
            # Display data summary
            summary = sentiment_result.get("data_summary", {})
            if summary:
                print("\nData Summary:")
                for source, stats in summary.items():
                    source_name = source.replace("_", " ").title()
                    if "reviews" in stats:
                        print(f"  {source_name}: {stats.get('analyzed_reviews', 0)} reviews analyzed out of {stats.get('total_reviews', 0)} total")
                    elif "topics" in stats or "discussions" in stats:
                        analyzed = stats.get("analyzed_items", 0)
                        total = (stats.get("total_topics", 0) + stats.get("total_discussions", 0))
                        print(f"  {source_name}: {analyzed} items analyzed out of {total} total")
                print()
    else:
        print("\nNo valid results to analyze.")
    
    print(f"{'=' * 60}")
    print("All tasks completed!")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
