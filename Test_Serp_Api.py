import asyncio
import os
import time
import json
from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import google.generativeai as genai

# API Keys
SERPAPI_KEY = os.getenv('SERPAPI_KEY')
if not SERPAPI_KEY:
    raise RuntimeError("SERPAPI_KEY not set")

# GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
# if not GEMINI_API_KEY:
#     raise RuntimeError("GEMINI_API_KEY not set")

# # Initialize Gemini
# genai.configure(api_key=GEMINI_API_KEY)

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
# Task 4: Gemini API Sentiment Analysis
# ============================================================================
async def analyze_sentiment_with_gemini(all_results: list) -> dict:
    """
    Analyze sentiment of combined scraped data from all sources using Gemini API.
    
    Args:
        all_results: List of dictionaries containing scraped data from all sources
    
    Returns:
        Dictionary containing combined sentiment analysis results
    """
    print(f"\n[Gemini] Starting combined sentiment analysis for {len(all_results)} source(s)")
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Filter out results with errors
        valid_results = [r for r in all_results if r and not r.get("error")]
        
        if not valid_results:
            return {
                "error": "No valid data to analyze",
                "sources": []
            }
        
        # Build combined prompt with data from all sources
        combined_sections = []
        data_summary = {}
        
        for data in valid_results:
            source = data.get("source", "unknown")
            section_content = []
            
            if source == "google_play_store":
                reviews = data.get("reviews", [])
                if reviews:
                    section_content.append("=== GOOGLE PLAY STORE REVIEWS ===")
                    section_content.append(f"Product ID: {data.get('product_id', 'N/A')}")
                    section_content.append(f"Platform: {data.get('platform', 'N/A')}")
                    section_content.append(f"Total Reviews: {len(reviews)}")
                    section_content.append("\nSample Reviews (first 50):")
                    for r in reviews[:50]:
                        rating = r.get('rating', 'N/A')
                        snippet = r.get('snippet', '')
                        section_content.append(f"Rating: {rating}/5 - {snippet}")
                    
                    data_summary["google_play_store"] = {
                        "total_reviews": len(reviews),
                        "analyzed_reviews": min(50, len(reviews))
                    }
            
            elif source == "apple_app_store":
                reviews = data.get("reviews", [])
                if reviews:
                    section_content.append("\n=== APPLE APP STORE REVIEWS ===")
                    section_content.append(f"Product ID: {data.get('product_id', 'N/A')}")
                    section_content.append(f"Country: {data.get('country', 'N/A')}")
                    section_content.append(f"Total Reviews: {len(reviews)}")
                    section_content.append("\nSample Reviews (first 50):")
                    for r in reviews[:50]:
                        rating = r.get('rating', 'N/A')
                        title = r.get('title', '')
                        text = r.get('text', '')
                        section_content.append(f"Rating: {rating}/5 - Title: {title} - Review: {text}")
                    
                    data_summary["apple_app_store"] = {
                        "total_reviews": len(reviews),
                        "analyzed_reviews": min(50, len(reviews))
                    }
            
            elif source == "reddit":
                reddit_data = data.get("data", [])
                if reddit_data:
                    section_content.append("\n=== REDDIT DISCUSSIONS AND TOPICS ===")
                    section_content.append(f"Subreddit: {data.get('topic', 'N/A')}")
                    section_content.append(f"Keywords: {', '.join(data.get('keywords', []))}")
                    
                    all_text = []
                    for subreddit_data in reddit_data:
                        for topic in subreddit_data.get("found_topics", []):
                            all_text.append(f"Topic: {topic.get('title', '')}")
                        for discussion in subreddit_data.get("discussions", [])[:20]:
                            all_text.append(f"Discussion: {discussion.get('title', '')}")
                    
                    section_content.append(f"\nTotal Topics: {data.get('total_topics', 0)}")
                    section_content.append(f"Total Discussions: {data.get('total_discussions', 0)}")
                    section_content.append("\nSample Content (first 100 items):")
                    section_content.extend(all_text[:100])
                    
                    data_summary["reddit"] = {
                        "total_topics": data.get("total_topics", 0),
                        "total_discussions": data.get("total_discussions", 0),
                        "analyzed_items": min(100, len(all_text))
                    }
            
            if section_content:
                combined_sections.append("\n".join(section_content))
        
        if not combined_sections:
            return {
                "error": "No text data to analyze from any source",
                "sources": [r.get("source") for r in valid_results]
            }
        
        # Create combined prompt
        combined_text = "\n\n".join(combined_sections)
        
        prompt = f"""Analyze the sentiment of the following combined data from multiple sources (Google Play Store, Apple App Store, and/or Reddit).

Provide a comprehensive sentiment analysis that includes:

1. OVERALL COMBINED SENTIMENT: 
   - Overall sentiment across all sources (positive/negative/neutral)
   - Sentiment distribution (percentage of positive, negative, neutral)

2. SOURCE-SPECIFIC ANALYSIS:
   - For each source present, provide:
     * Sentiment breakdown
     * Key positive points
     * Key negative points
     * Common themes

3. CROSS-SOURCE INSIGHTS:
   - Compare sentiment patterns across different sources
   - Identify common themes that appear across multiple sources
   - Highlight any conflicting sentiments between sources

4. SUMMARY AND RECOMMENDATIONS:
   - Overall assessment
   - Key takeaways
   - Actionable insights

DATA FROM ALL SOURCES:
{combined_text}

Please provide a detailed, structured analysis covering all the above points."""
        
        # Run async call to Gemini
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: model.generate_content(prompt)
        )
        
        analysis_text = response.text
        
        sources_analyzed = [r.get("source") for r in valid_results]
        print(f"[Gemini] Combined sentiment analysis completed for sources: {', '.join(sources_analyzed)}")
        
        return {
            "sources": sources_analyzed,
            "sentiment_analysis": analysis_text,
            "data_summary": data_summary
        }
    
    except Exception as e:
        print(f"[Gemini] Error during sentiment analysis: {e}")
        return {
            "error": str(e),
            "sources": [r.get("source") for r in all_results if r and not r.get("error")]
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
        # output_filename = "scraped_data.json"
        # with open(output_filename, "w", encoding="utf-8") as f:
        #     json.dump(valid_results, f, indent=2, ensure_ascii=False)
        # print(f"\nScraped data saved to {output_filename}")
        # print(f"Total sources: {len(valid_results)}")
        
        # Commented out Gemini API call for testing
        # print(f"Combining results for sentiment analysis...")
        # sentiment_result = await analyze_sentiment_with_gemini(valid_results)
        # 
        # # Display combined results
        # print(f"\n{'=' * 60}")
        # print("COMBINED SENTIMENT ANALYSIS RESULTS")
        # print(f"{'=' * 60}\n")
        # 
        # if sentiment_result.get("error"):
        #     print(f"Error in sentiment analysis: {sentiment_result['error']}\n")
        # else:
        #     sources = sentiment_result.get("sources", [])
        #     print(f"Sources analyzed: {', '.join([s.replace('_', ' ').title() for s in sources])}\n")
        #     print("-" * 60)
        #     print(sentiment_result.get("sentiment_analysis", "No analysis available"))
        #     print("-" * 60)
        #     
        #     # Display data summary
        #     summary = sentiment_result.get("data_summary", {})
        #     if summary:
        #         print("\nData Summary:")
        #         for source, stats in summary.items():
        #             source_name = source.replace("_", " ").title()
        #             if "reviews" in stats:
        #                 print(f"  {source_name}: {stats.get('analyzed_reviews', 0)} reviews analyzed out of {stats.get('total_reviews', 0)} total")
        #             elif "topics" in stats or "discussions" in stats:
        #                 analyzed = stats.get("analyzed_items", 0)
        #                 total = (stats.get("total_topics", 0) + stats.get("total_discussions", 0))
        #                 print(f"  {source_name}: {analyzed} items analyzed out of {total} total")
        #         print()
    else:
        print("\nNo valid results to analyze.")
    
    print(f"{'=' * 60}")
    print("All tasks completed!")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
