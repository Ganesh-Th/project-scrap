import asyncio
import os
import time
import json
import random
from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup
from google import genai as genai_new
from google.genai import types

# API Keys
SERPAPI_KEY = os.getenv('SERPAPI_KEY')
if not SERPAPI_KEY:
    raise RuntimeError("SERPAPI_KEY not set")

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set")

# ============================================================================
# Helper Function: Create Gemini Client with URL Context and Google Search
# ============================================================================
def create_gemini_client_with_tools():
    """
    Create a new Gemini client with URL Context and Google Search capability.
    
    Returns:
        Tuple of (client, model_name, config)
    """
    client = genai_new.Client(api_key=GEMINI_API_KEY)
    model_name = "gemini-2.5-flash-lite"
    
    # Configure tools: URL context for Google Search links + Google Search for social media
    tools = [
        types.Tool(url_context=types.UrlContext()),
        types.Tool(googleSearch=types.GoogleSearch()),
    ]
    
    # Configure generation settings
    generate_config = types.GenerateContentConfig(
        tools=tools,
    )
    
    return client, model_name, generate_config

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
async def scrape_google_play_reviews(product_id: str, platform: str) -> tuple:
    """
    Scrape Google Play Store reviews.
    
    Args:
        product_id: Google Play Store product ID (e.g., com.google.android.youtube)
        platform: Platform type (phone/tablet/tv/wearables/auto/chromebook)
    
    Returns:
        tuple: (source, product_id, platform, reviews_json, total_reviews)
            - source: "google_play_store"
            - product_id: The product ID
            - platform: The platform type
            - reviews_json: List of review dictionaries (to be converted to TOON)
            - total_reviews: Number of reviews fetched
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
        "json_restrictor": "reviews[].{rating, snippet, likes, iso_date}",
        "api_key": SERPAPI_KEY
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        reviews = results.get("reviews", [])
        
        print(f"[Google Play Store] Successfully fetched {len(reviews)} reviews")
        
        return (
            "google_play_store",
            product_id,
            platform,
            reviews,
            len(reviews)
        )
    except Exception as e:
        print(f"[Google Play Store] Error: {e}")
        return (
            "google_play_store",
            product_id,
            platform,
            [],
            0
        )


# ============================================================================
# Task 2: Apple App Store Reviews Scraper
# ============================================================================
async def scrape_apple_store_reviews(product_id: str, country: str, target_reviews: int = 199) -> tuple:
    """
    Scrape Apple App Store reviews.
    
    Args:
        product_id: Apple App Store product ID (e.g., 544007664)
        country: Country code (e.g., us, gb, ca)
        target_reviews: Target number of reviews to fetch (default: 199)
    
    Returns:
        tuple: (source, product_id, country, reviews_json, total_reviews)
            - source: "apple_app_store"
            - product_id: The product ID
            - country: The country code
            - reviews_json: List of review dictionaries (to be converted to TOON)
            - total_reviews: Number of reviews fetched
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
                "json_restrictor": "reviews[].{title, text, rating, review_date, reviewed_version}, serpapi_pagination",
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
        
        return (
            "apple_app_store",
            product_id,
            country,
            all_reviews,
            len(all_reviews)
        )
    except Exception as e:
        print(f"[Apple App Store] Error: {e}")
        return (
            "apple_app_store",
            product_id,
            country,
            [],
            0
        )


# ============================================================================
# Helper Function: Scrape Reddit Thread Details
# ============================================================================
def scrape_reddit_thread_details(session, thread_url):
    """
    Visits a specific thread URL to extract the body text and comments.
    
    Args:
        session: requests.Session object
        thread_url: URL of the Reddit thread
    
    Returns:
        dict with keys: title, posted, comment_count_stat, body_text, comments_content
    """
    print(f"      -> Visiting thread: {thread_url[:60]}...")
    try:
        time.sleep(random.uniform(2, 4))  # Random sleep to avoid rate limiting
        
        response = session.get(thread_url, headers={
            'User-Agent': random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
            ]),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }, timeout=10)
        
        if response.status_code != 200:
            return {
                "title": "[Error: Could not load]",
                "posted": "Unknown",
                "comment_count_stat": "0",
                "body_text": "[Error: Could not load]",
                "comments_content": []
            }

        soup = BeautifulSoup(response.content, "html.parser")

        # Extract title
        title = ""
        title_tag = soup.find("a", class_="title")
        if title_tag:
            title = title_tag.get_text(strip=True)

        # Extract posted time
        posted = ""
        time_tag = soup.find("time")
        if time_tag:
            posted = time_tag.get("title", time_tag.get_text(strip=True))

        # Extract comment count
        comment_count = "0"
        
        # 1. Extract Post Body
        body_text = ""
        main_post = soup.find("div", class_="link")
        if main_post:
            usertext = main_post.find("div", class_="usertext-body")
            if usertext:
                body_text = usertext.get_text(separator="\n", strip=True)

        # 2. Extract Comments
        comments_data = []
        comment_area = soup.find("div", class_="commentarea")
        if comment_area:
            # Limit to top 20 comments
            all_comments = comment_area.find_all("div", class_="entry", limit=20) 
            
            for comment in all_comments:
                try:
                    text_div = comment.find("div", class_="usertext-body")
                    text = text_div.get_text(strip=True) if text_div else ""
                    
                    if text:
                        comments_data.append({
                            "text": text
                        })
                except:
                    continue
            
            comment_count = str(len(comments_data))

        return {
            "title": title,
            "posted": posted,
            "comment_count_stat": comment_count,
            "body_text": body_text,
            "comments_content": comments_data
        }

    except Exception as e:
        print(f"      !!! Error reading thread details: {e}")
        return {
            "title": "[Error]",
            "posted": "Unknown",
            "comment_count_stat": "0",
            "body_text": "[Error]",
            "comments_content": []
        }


# ============================================================================
# Task 3: Reddit Scraper (using old.reddit.com keyword search)
# ============================================================================
async def scrape_reddit(keyword: str, limit_pages: int = 2) -> tuple:
    """
    Scrape Reddit using keyword search on old.reddit.com with full content extraction.
    
    Args:
        keyword: Single keyword to search for (will have " Review" appended)
        limit_pages: Maximum pages to scrape (default: 2)
    
    Returns:
        tuple: (source, keyword, scraped_posts_list, total_posts)
            - source: "reddit"
            - keyword: The keyword used for search
            - scraped_posts_list: List of post dictionaries with full content
            - total_posts: Number of posts scraped
    """
    # Append " Review" to the keyword for Reddit search
    search_keyword = f"{keyword.strip()} Review"
    print(f"\n[Reddit] Starting keyword search for: {search_keyword}")
    
    base_url = "https://old.reddit.com/search"
    all_urls = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f'[Reddit] --- Starting search for: "{search_keyword}" ---')
    
    # Use relevance sort and filter by month
    current_url = f"{base_url}?q={search_keyword}&sort=relevance&t=month"
    
    page_counter = 0
    
    # Step 1: Collect URLs
    while current_url and page_counter < limit_pages:
            page_counter += 1
            print(f"[Reddit]    Scraping Page {page_counter}...")
            
            try:
                response = requests.get(current_url, headers=headers, timeout=10)
                
                # Handle rate limiting
                if response.status_code == 429:
                    print("[Reddit]    !!! Rate limit hit (429). Sleeping for 30 seconds...")
                    await asyncio.sleep(30)
                    continue
                
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, "html.parser")
                
                results = soup.find_all("div", class_="search-result")
                
                if not results:
                    print("[Reddit]    No results found on this page.")
                    break
                
                for result in results:
                    title_tag = result.find("a", class_="search-title")
                    
                    if title_tag:
                        href = title_tag["href"]
                        
                        if href.startswith("/"):
                            href = f"https://old.reddit.com{href}"
                        
                        # Skip user profiles
                        if "/user/" not in href:
                            all_urls.append(href)
                
                # Pagination logic
                next_button = soup.find("span", class_="nextprev")
                next_link = None
                
                if next_button:
                    for link in next_button.find_all("a"):
                        if "next" in link.get_text(strip=True).lower():
                            next_link = link["href"]
                            break
                
                if next_link:
                    # Handle relative URLs
                    if next_link.startswith("/"):
                        next_link = f"https://old.reddit.com{next_link}"
                    
                    current_url = next_link
                    await asyncio.sleep(2)  # Rate limiting delay
                else:
                    print(f"[Reddit]    Reached last page (No 'Next' button found on Page {page_counter}).")
                    current_url = None
            
            except Exception as e:
                print(f'[Reddit]    Error on page {page_counter}: {e}')
                break
    
    print(f"[Reddit] Found {len(all_urls)} URLs. Now scraping full content...")
    
    # Step 2: Scrape full content from each URL
    session = requests.Session()
    scraped_posts = []
    
    for url in all_urls:
        post_data = scrape_reddit_thread_details(session, url)
        post_data["url"] = url  # Add URL for reference
        scraped_posts.append(post_data)
    
    total_posts = len(scraped_posts)
    print(f"[Reddit] Successfully scraped {total_posts} posts with full content for keyword: {search_keyword}")
    
    return (
        "reddit",
        search_keyword,
        scraped_posts,
        total_posts
    )


# ============================================================================
# Task 4: Google Search Scraper
# ============================================================================
async def scrape_google_search(product_name: str) -> tuple:
    """
    Scrape Google search results for product reviews using SerpAPI.
    
    Args:
        product_name: Name of the product to search for reviews
    
    Returns:
        tuple: (source, query, results_json, total_results)
            - source: "google_search"
            - query: The search query used
            - results_json: List of result dictionaries with link, snippet, source, 
                           and optionally rich_snippet and sitelinks
            - total_results: Number of results fetched
    """
    query = f"{product_name} Review"
    print(f"\n[Google Search] Starting search for: {query}")
    
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        organic_results = results.get("organic_results", [])
        
        # Extract relevant fields from each result
        processed_results = []
        
        for result in organic_results:
            result_data = {
                "link": result.get("link", ""),
                "snippet": result.get("snippet", ""),
                "source": result.get("source", "")
            }
            
            # Add rich_snippet if available
            if "rich_snippet" in result:
                result_data["rich_snippet"] = result.get("rich_snippet")
            
            # Add sitelinks if available
            if "sitelinks" in result:
                result_data["sitelinks"] = result.get("sitelinks")
            
            processed_results.append(result_data)
        
        print(f"[Google Search] Successfully fetched {len(processed_results)} results")
        
        return (
            "google_search",
            query,
            processed_results,
            len(processed_results)
        )
    except Exception as e:
        print(f"[Google Search] Error: {e}")
        return (
            "google_search",
            query,
            [],
            0
        )


# ============================================================================
# Helper Function: Convert Reviews JSON to TOON Format
# ============================================================================
def convert_reviews_to_toon(reviews: list, source_type: str) -> str:
    """
    Convert reviews JSON list to TOON format.
    
    Args:
        reviews: List of review dictionaries
        source_type: "google_play_store", "apple_app_store", "reddit", or "google_search"
    
    Returns:
        TOON formatted string with header and data rows
    """
    if not reviews:
        return ""
    
    if source_type == "google_play_store":
        header = "rating | snippet | likes | iso_date"
        rows = [header]
        for review in reviews:
            snippet = str(review.get("snippet", "")).replace("|", " ").replace("\n", " ").replace("\r", " ")
            row = f"{review.get('rating', '')} | {snippet} | {review.get('likes', '')} | {review.get('iso_date', '')}"
            rows.append(row)
        return "\n".join(rows)
    
    elif source_type == "apple_app_store":
        header = "title | text | rating | review_date | reviewed_version"
        rows = [header]
        for review in reviews:
            title = str(review.get("title", "")).replace("|", " ").replace("\n", " ").replace("\r", " ")
            text = str(review.get("text", "")).replace("|", " ").replace("\n", " ").replace("\r", " ")
            row = f"{title} | {text} | {review.get('rating', '')} | {review.get('review_date', '')} | {review.get('reviewed_version', '')}"
            rows.append(row)
        return "\n".join(rows)
    
    elif source_type == "reddit":
        # New format: title | posted | comment_count_stat | body_text | comments_text
        header = "title | posted | comment_count_stat | body_text | comments_text"
        rows = [header]
        for post in reviews:
            title = str(post.get("title", "")).replace("|", " ").replace("\n", " ").replace("\r", " ")
            posted = str(post.get("posted", "")).replace("|", " ").replace("\n", " ").replace("\r", " ")
            comment_count = str(post.get("comment_count_stat", "")).replace("|", " ")
            body_text = str(post.get("body_text", "")).replace("|", " ").replace("\n", " ").replace("\r", " ")
            
            # Extract only text field from comments_content
            comments_texts = [str(c.get("text", "")).replace("|", " ").replace("\n", " ").replace("\r", " ") 
                             for c in post.get("comments_content", [])]
            comments_combined = " | ".join(comments_texts) if comments_texts else ""
            
            row = f"{title} | {posted} | {comment_count} | {body_text} | {comments_combined}"
            rows.append(row)
        return "\n".join(rows)
    
    elif source_type == "google_search":
        header = "link | snippet | source | rich_snippet | sitelinks"
        rows = [header]
        for result in reviews:
            snippet = str(result.get("snippet", "")).replace("|", " ").replace("\n", " ").replace("\r", " ")
            
            # Convert nested structures to JSON strings
            rich_snippet_str = json.dumps(result.get("rich_snippet")) if "rich_snippet" in result else ""
            sitelinks_str = json.dumps(result.get("sitelinks")) if "sitelinks" in result else ""
            
            row = f"{result.get('link', '')} | {snippet} | {result.get('source', '')} | {rich_snippet_str} | {sitelinks_str}"
            rows.append(row)
        return "\n".join(rows)
    
    return ""


# ============================================================================
# Helper Function: Parse TOON Findings into Structured JSON
# ============================================================================
def _parse_toon_findings(toon_text: str, scrape_results: list, data_summary: dict) -> dict:
    """
    Parse TOON findings into structured JSON format with partial parsing support.
    
    Args:
        toon_text: TOON-formatted findings from Gemini
        scrape_results: List of tuples from scrape functions (for rating calculation)
        data_summary: Data summary dictionary
    
    Returns:
        Structured sentiment analysis dictionary
    """
    print(f"[TOON Parser] Starting TOON parsing...")
    
    # Schema: type | category | title | description | frequency | severity | sample_reviews | recommendation | priority_score | sources
    lines = toon_text.strip().split('\n')
    
    if not lines:
        print(f"[TOON Parser] Error: Empty TOON text")
        return None
    
    # Find header line
    header_idx = -1
    for i, line in enumerate(lines):
        if 'type' in line.lower() and 'category' in line.lower() and 'title' in line.lower():
            header_idx = i
            break
    
    if header_idx == -1:
        print(f"[TOON Parser] Warning: No header found, assuming first line is header")
        header_idx = 0
    
    # Parse findings
    findings = []
    skipped_rows = 0
    
    for line_num, line in enumerate(lines[header_idx + 1:], start=header_idx + 2):
        line = line.strip()
        if not line:
            continue
        
        # Split by pipe delimiter
        parts = [p.strip() for p in line.split('|')]
        
        if len(parts) < 3:  # Need at least type, category, title
            print(f"[TOON Parser] Warning: Skipping malformed row {line_num} (too few columns): {line[:100]}")
            skipped_rows += 1
            continue
        
        try:
            # Extract fields with defaults
            finding_type = parts[0] if len(parts) > 0 else "pain_point"
            category = parts[1] if len(parts) > 1 else "other"
            title = parts[2] if len(parts) > 2 else "Untitled"
            description = parts[3] if len(parts) > 3 else ""
            
            # Parse frequency
            frequency_str = parts[4] if len(parts) > 4 else "1"
            try:
                frequency = int(frequency_str.strip())
            except (ValueError, AttributeError):
                frequency = 1
            
            # Parse severity
            severity = parts[5] if len(parts) > 5 else "medium"
            severity = severity.strip().lower()
            if severity not in ["critical", "high", "medium", "low"]:
                severity = "medium"
            
            # Parse sample_reviews (semicolon-separated)
            sample_reviews_str = parts[6] if len(parts) > 6 else ""
            try:
                sample_reviews = json.loads(sample_reviews_str)
    
                # Optional: Clean up any remaining artifacts if Gemini was extra messy
                sample_reviews = [s.replace('[PIPE]', '|') for s in sample_reviews]
    
            except json.JSONDecodeError:
    
                sample_reviews = [
                    s.strip().strip('\\"').strip('"').replace('[PIPE]', '|') 
                    for s in sample_reviews_str.split(',') 
                    if s.strip()
                ]

            # Parse recommendation
            recommendation = parts[7] if len(parts) > 7 else ""
            recommendation = recommendation.replace('[PIPE]', '|')
            
            # Parse priority_score
            priority_str = parts[8] if len(parts) > 8 else "5"
            try:
                priority_score = int(priority_str.strip())
            except (ValueError, AttributeError):
                priority_score = 5
            
            # Parse sources (comma-separated)
            sources_str = parts[9] if len(parts) > 9 else ""
            sources = [s.strip() for s in sources_str.split(',') if s.strip()]
            
            # Replace [PIPE] in text fields
            title = title.replace('[PIPE]', '|')
            description = description.replace('[PIPE]', '|')
            
            finding = {
                "type": finding_type.strip(),
                "category": category,
                "title": title,
                "description": description,
                "frequency": frequency,
                "severity": severity,
                "sample_reviews": sample_reviews[:3],  # Limit to 3
                "recommendation": recommendation,
                "priority_score": priority_score,
                "sources": sources
            }
            
            findings.append(finding)
            
        except Exception as e:
            print(f"[TOON Parser] Warning: Error parsing row {line_num}: {e}")
            skipped_rows += 1
            continue
    
    print(f"[TOON Parser] Parsed {len(findings)} findings, skipped {skipped_rows} malformed rows")
    
    if not findings:
        print(f"[TOON Parser] Error: No valid findings parsed")
        return None
    
    # Group findings by type
    bugs = [f for f in findings if f["type"] == "bug"]
    feature_requests = [f for f in findings if f["type"] == "feature_request"]
    requirements = [f for f in findings if f["type"] == "requirement"]
    usability_frictions = [f for f in findings if f["type"] == "usability_friction"]
    pain_points = [f for f in findings if f["type"] == "pain_point"]
    positive_reviews = [f for f in findings if f["type"] == "positive_review"]
    ai_insights = [f for f in findings if f["type"] == "ai_insight"]
    
    # Calculate overall sentiment from frequency distribution
    total_positive = sum(f["frequency"] for f in positive_reviews)
    total_negative = sum(f["frequency"] for f in bugs) + sum(f["frequency"] for f in pain_points)
    total_neutral = sum(f["frequency"] for f in feature_requests) + sum(f["frequency"] for f in requirements)
    total_sentiment = total_positive + total_negative + total_neutral
    
    if total_sentiment > 0:
        positive_pct = (total_positive / total_sentiment) * 100
        negative_pct = (total_negative / total_sentiment) * 100
        neutral_pct = (total_neutral / total_sentiment) * 100
    else:
        positive_pct = negative_pct = neutral_pct = 33.3
    
    # Calculate average rating from reviews
    ratings = []
    for result in scrape_results:
        source = result[0]
        if source == "google_play_store":
            reviews = result[3]
            for r in reviews:
                rating = r.get("rating")
                if rating:
                    ratings.append(float(rating))
        elif source == "apple_app_store":
            reviews = result[3]
            for r in reviews:
                rating = r.get("rating")
                if rating:
                    ratings.append(float(rating))
    
    avg_rating = sum(ratings) / len(ratings) if ratings else 0
    
    # Calculate total reviews analyzed
    total_reviews = 0
    for source, stats in data_summary.items():
        if "analyzed_reviews" in stats:
            total_reviews += stats.get("analyzed_reviews", 0)
        elif "analyzed_items" in stats:
            total_reviews += stats.get("analyzed_items", 0)
    
    # Build priority actions from top findings
    priority_actions = []
    
    # Add critical bugs
    critical_bugs = sorted([f for f in bugs if f["severity"] == "critical"], 
                          key=lambda x: x["priority_score"], reverse=True)[:3]
    for bug in critical_bugs:
        priority_actions.append({
            "action": f"Fix critical bug: {bug['title']}",
            "reason": f"Critical severity with {bug['frequency']} mentions - impacts core functionality",
            "expected_impact": "high",
            "effort_required": "high"
        })
    
    # Add top requirements
    top_requirements = sorted(requirements, key=lambda x: x["priority_score"], reverse=True)[:2]
    for req in top_requirements:
        priority_actions.append({
            "action": f"Implement required feature: {req['title']}",
            "reason": f"Expected by users ({req['frequency']} mentions) - missing essential functionality",
            "expected_impact": "high",
            "effort_required": "medium"
        })
    
    # Add top usability frictions
    top_frictions = sorted(usability_frictions, key=lambda x: x["priority_score"], reverse=True)[:2]
    for friction in top_frictions:
        priority_actions.append({
            "action": f"Fix UX issue: {friction['title']}",
            "reason": f"Causes user frustration ({friction['frequency']} mentions) - UX improvement",
            "expected_impact": "medium",
            "effort_required": "low"
        })
    
    priority_actions = priority_actions[:7]
    
    # Build key insights
    key_insights = []
    
    if bugs:
        key_insights.append(f"Found {len(bugs)} bugs, {len(critical_bugs)} critical. Top issue: {bugs[0]['title']} ({bugs[0]['frequency']} mentions)")
    
    if feature_requests:
        top_feature = sorted(feature_requests, key=lambda x: x["frequency"], reverse=True)[0]
        key_insights.append(f"Top feature request: {top_feature['title']} ({top_feature['frequency']} mentions)")
    
    if positive_reviews:
        top_positive = sorted(positive_reviews, key=lambda x: x["frequency"], reverse=True)[0]
        key_insights.append(f"Users love: {top_positive['title']} ({top_positive['frequency']} mentions)")
    
    key_insights.append(f"Overall sentiment: {round(positive_pct, 1)}% positive, {round(negative_pct, 1)}% negative")
    
    if ai_insights:
        key_insights.append(f"AI identified {len(ai_insights)} patterns/correlations across sources")
    
    # Build final analysis
    analysis = {
        "overall_sentiment": {
            "positive_percentage": round(positive_pct, 1),
            "negative_percentage": round(negative_pct, 1),
            "neutral_percentage": round(neutral_pct, 1),
            "average_rating": round(avg_rating, 2),
            "total_reviews_analyzed": total_reviews
        },
        "bugs": bugs,
        "feature_requests": feature_requests,
        "requirements": requirements,
        "usability_frictions": usability_frictions,
        "pain_points": pain_points,
        "positive_reviews": positive_reviews,
        "ai_insights": ai_insights,
        "priority_actions": priority_actions,
        "key_insights": key_insights
    }
    
    print(f"[TOON Parser] Successfully parsed into structured analysis:")
    print(f"[TOON Parser]   - Bugs: {len(bugs)}, Features: {len(feature_requests)}, Requirements: {len(requirements)}")
    print(f"[TOON Parser]   - Usability: {len(usability_frictions)}, Pain Points: {len(pain_points)}")
    print(f"[TOON Parser]   - Positive: {len(positive_reviews)}, AI Insights: {len(ai_insights)}")
    
    return analysis


# ============================================================================
# Helper Function: Build Combined Query for Gemini API
# ============================================================================
def build_gemini_query(scrape_results: list) -> tuple[str, dict]:
    """
    Build the combined query string for Gemini API.
    Combines metadata and TOON-formatted reviews from all sources.
    
    Args:
        scrape_results: List of tuples from scrape functions
            - Google Play: (source, product_id, platform, reviews, total_reviews)
            - Apple Store: (source, product_id, country, reviews, total_reviews)
            - Reddit: (source, keyword, url_list, total_urls)
            - Google Search: (source, query, results, total_results)
    
    Returns:
        Tuple of (combined_query: str, data_summary: dict)
    """
    if not scrape_results:
        return "", {}
    
    sections = []
    data_summary = {}
    
    for result in scrape_results:
        source = result[0]
        
        if source == "google_play_store":
            _, product_id, platform, reviews, total_reviews = result
            reviews_toon = convert_reviews_to_toon(reviews, "google_play_store")
            
            section = f"""=== GOOGLE PLAY STORE REVIEWS ===
Source: {source}
Product ID: {product_id}
Platform: {platform}
Total Reviews: {total_reviews}

Reviews (TOON format):
{reviews_toon}"""
            sections.append(section)
            
            data_summary[source] = {
                "total_reviews": total_reviews,
                "analyzed_reviews": total_reviews
            }
        
        elif source == "apple_app_store":
            _, product_id, country, reviews, total_reviews = result
            reviews_toon = convert_reviews_to_toon(reviews, "apple_app_store")
            
            section = f"""=== APPLE APP STORE REVIEWS ===
Source: {source}
Product ID: {product_id}
Country: {country}
Total Reviews: {total_reviews}

Reviews (TOON format):
{reviews_toon}"""
            sections.append(section)
            
            data_summary[source] = {
                "total_reviews": total_reviews,
                "analyzed_reviews": total_reviews
            }
        
        elif source == "reddit":
            _, keyword, urls, total_urls = result
            urls_toon = convert_reviews_to_toon(urls, "reddit")
            
            section = f"""=== REDDIT URLS ===
Source: {source}
Keyword: {keyword}
Total URLs: {total_urls}

URLs (TOON format):
{urls_toon}"""
            sections.append(section)
            
            data_summary[source] = {
                "total_urls": total_urls,
                "analyzed_items": total_urls
            }
        
        elif source == "google_search":
            _, query, results, total_results = result
            results_toon = convert_reviews_to_toon(results, "google_search")
            
            section = f"""=== GOOGLE SEARCH RESULTS ===
Source: {source}
Query: {query}
Total Results: {total_results}

Results (TOON format):
{results_toon}"""
            sections.append(section)
            
            data_summary[source] = {
                "total_results": total_results,
                "analyzed_items": total_results
            }
    
    combined_query = "\n\n".join(sections)
    
    return combined_query, data_summary


# ============================================================================
# Helper Function: Batch URLs for Processing
# ============================================================================


# ============================================================================
# Helper Function: Extract Google Search URLs
# ============================================================================
def extract_google_search_urls(scrape_results: list, max_urls: int = 15) -> list:
    """
    Extract URLs from Google Search results only (not Reddit).
    
    Args:
        scrape_results: List of tuples from scrape functions
        max_urls: Maximum URLs to extract (default: 15)
    
    Returns:
        List of URL strings from Google Search results
    """
    urls = []
    
    for result in scrape_results:
        source = result[0]
        
        if source == "google_search":
            # tuple: (source, query, results_json, total_results)
            results = result[2]
            for res in results:
                url = res.get("link", "")
                if url and url not in urls:
                    urls.append(url)
                    if len(urls) >= max_urls:
                        break
        
        if len(urls) >= max_urls:
            break
    
    return urls[:max_urls]


# ============================================================================
# Task 4: Gemini API Sentiment Analysis (Enhanced with AI Categorization)
# ============================================================================
async def analyze_sentiment_with_gemini(combined_query: str, data_summary: dict, scrape_results: list, product_name: str = "", max_urls_per_batch: int = 20) -> dict:
    """
    Analyze sentiment of combined scraped data from all sources using Gemini API
    with URL context and Google Search capabilities.
    
    Enhanced Features:
    - Access and analyze content from URLs directly
    - Search social media for additional product reviews
    - Categorize findings into 7 types: bugs, feature_requests, requirements,
      usability_frictions, pain_points, positive_reviews, ai_insights
    
    Args:
        combined_query: Combined query string with metadata and TOON-formatted reviews
        data_summary: Dictionary containing summary of data from each source
        scrape_results: List of tuples from scrape functions (for extracting ratings)
        product_name: Product name for social media search
        max_urls_per_batch: Maximum URLs to process per batch (default: 20)
    
    Returns:
        Dictionary containing comprehensive sentiment analysis with 7-type categorization
    """
    # Identify sources from scrape_results
    sources = [result[0] for result in scrape_results if result]
    print(f"\n[Gemini] Starting sentiment analysis for {len(sources)} source(s)")
    
    try:
        # Create Gemini client
        client, model_name, generate_config = create_gemini_client_with_tools()
        
        if not combined_query:
            return {
                "error": "No text data to analyze from any source",
                "sources": sources
            }
        
        # Use combined_query directly (already formatted efficiently with metadata + TOON)
        combined_text = combined_query
        
        # Estimate token count (rough: 1 token ≈ 4 characters)
        estimated_tokens = len(combined_text) // 4
        print(f"[Gemini] Estimated input tokens: ~{estimated_tokens}")
        
        # If data is too large, use batch processing
        MAX_TOKENS_PER_REQUEST = 200000
        
        if estimated_tokens > MAX_TOKENS_PER_REQUEST:
            print(f"[Gemini] Large dataset detected. Using batch processing...")
            return await _analyze_sentiment_batch_processing(model_name, scrape_results, combined_text, data_summary, product_name, max_urls_per_batch)
        
        # Extract Google Search URLs (limit to 15)
        google_urls = extract_google_search_urls(scrape_results, max_urls=15)
        
        # Build URLs section for Google Search results
        urls_section = ""
        if google_urls:
            urls_list = "\n".join([f"- {url}" for url in google_urls])
            urls_section = f"""

GOOGLE SEARCH URLs TO ANALYZE (Visit these URLs using URL context and extract review content):
{urls_list}
"""
        
        # Build social media search instruction
        social_search_instruction = ""
        if product_name:
            social_search_instruction = f"""

SOCIAL MEDIA SEARCH:
Search for "{product_name} review" on relevant social media platforms (Twitter/X, Facebook, Instagram, Reddit, etc.).
Choose platforms based on the product type and where reviews are likely to be found.
Include findings from social media in your analysis.
"""
        
        print(f"[Gemini] Google Search URLs to analyze: {len(google_urls)}")
        
        prompt = f"""You are an expert app analyst specializing in user feedback analysis.

CRITICAL: Output ONLY in TOON (pipe-delimited) format. NO JSON, NO markdown, just the TOON table.

TASKS:
1. Analyze ALL reviews and discussions from all provided sources
2. Visit and analyze the Google Search URLs using your URL context tool to extract full review content
3. {f'Search social media for "{product_name} review" to gather additional user feedback' if product_name else 'Use only the provided data'}
4. Categorize EVERY finding into exactly ONE of these 7 types:
   - bug: Technical issues, crashes, errors, broken features
   - feature_request: User-requested new features or enhancements
   - requirement: Must-have features users expect but are missing
   - usability_friction: UX issues that frustrate users (confusing UI, too many steps, poor flow)
   - pain_point: General problems causing user dissatisfaction
   - positive_review: Things users love, praise, and appreciate
   - ai_insight: Patterns, trends, or correlations YOU identify by cross-referencing all sources
5. Generate AI insights by finding hidden patterns and correlations users don't explicitly state

IMPORTANT INSTRUCTIONS:
- Cross-reference findings across all sources
- Identify patterns (e.g., "Users who mention X also mention Y 70% of the time")
- Detect trends (e.g., "Bug reports increased after version update")
- Find platform-specific issues (e.g., "Android users report more crashes than iOS")

OUTPUT FORMAT (TOON - pipe-delimited):
type | category | title | description | frequency | severity | sample_reviews | recommendation | priority_score | sources

FORMATTING RULES:
- Start with the header row exactly as shown above
- One finding per line
- Use semicolons (;) to separate multiple sample_reviews
- Use commas (,) to separate multiple sources
- Replace any pipe characters (|) in text fields with [PIPE]
- Keep sample_reviews short (max 2-3 per finding)
- severity: use critical, high, medium, or low (omit for positive_review and feature_request)
- priority_score: 1-10, higher = more urgent
- sources: reddit, google_play_store, apple_app_store, google_search, or social_media

EXAMPLE ROWS:
bug | performance | App lagging and freezing | Users experiencing significant lag when opening videos | 35 | high | App gets freezed when I open a video; Always lagging and glitching | Optimize video playback and UI responsiveness | 9 | google_play_store,apple_app_store
positive_review | ui | Clean and intuitive interface | Users praise the app's simple and easy-to-use design | 28 | medium | Love the clean interface; So easy to navigate | Continue prioritizing user-friendly design | 7 | google_play_store,reddit

SCRAPED DATA FROM ALL SOURCES (TOON format):
{combined_text}
{urls_section}
{social_search_instruction}

Remember: 
1. Use your URL context tool to visit and analyze the Google Search URLs
2. {f'Search social media for "{product_name} review" to gather additional insights' if product_name else 'Use only the provided data'}
3. Analyze all provided text data
4. Output ONLY the TOON table (header + data rows)
5. NO JSON, NO markdown code blocks, NO explanations - just the pure TOON table"""
        
        # Create content with user prompt
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )
        ]
        
        print(f"[Gemini] Sending request to {model_name}...")
        
        # Run async streaming call to Gemini
        loop = asyncio.get_event_loop()
        
        def generate_content():
            response_text = ""
            for chunk in client.models.generate_content_stream(
                model=model_name,
                contents=contents,
                config=generate_config,
            ):
                if hasattr(chunk, 'text') and chunk.text:
                    response_text += chunk.text
            return response_text
        
        response_text = await loop.run_in_executor(None, generate_content)
        analysis_text = response_text.strip()
        
        # Parse TOON format response
        analysis_json = _parse_toon_findings(analysis_text, scrape_results, data_summary)
        
        if analysis_json is not None:
            print(f"[Gemini] Sentiment analysis completed for sources: {', '.join(sources)}")
            
            return {
                "sources": sources,
                "sentiment_analysis": analysis_json,
                "data_summary": data_summary,
                "processing_mode": "single_request"
            }
        
        # If parsing failed, return raw text for debugging
        print(f"[Gemini] Warning: Could not parse TOON response.")
        print(f"[Gemini] First 500 chars of response: {analysis_text[:500]}")
        return {
            "sources": sources,
            "sentiment_analysis": {"text": analysis_text},
            "data_summary": data_summary,
            "parse_error": "TOON parsing failed"
        }
    
    except Exception as e:
        print(f"[Gemini] Error during sentiment analysis: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "sources": sources if 'sources' in dir() else []
        }


async def _analyze_sentiment_batch_processing(model_name: str, scrape_results: list, toon_text: str, data_summary: dict, product_name: str = "", max_urls_per_batch: int = 20) -> dict:
    """
    Handle large datasets by processing in batches.
    Uses TOON format text directly (already formatted efficiently from all sources).
    
    Args:
        model_name: Gemini model name
        scrape_results: List of tuples from scrape functions
        toon_text: TOON format text (token-efficient format)
        data_summary: Dictionary with data summary
        product_name: Product name (unused, kept for compatibility)
        max_urls_per_batch: Unused, kept for compatibility
    
    Returns:
        Dictionary containing aggregated sentiment analysis results with 7-type categorization
    """
    print(f"[Gemini] Processing large dataset in batches...")
    
    # Create Gemini client
    client, model_name, generate_config = create_gemini_client_with_tools()
    
    # Extract Google Search URLs (limit to 15 for first batch only)
    google_urls = extract_google_search_urls(scrape_results, max_urls=15)
    
    # Use TOON text directly
    combined_text = toon_text
    total_size = len(combined_text)
    print(f"[Gemini] Total TOON text size: {total_size:,} characters (~{total_size // 4:,} tokens)")
    print(f"[Gemini] Google Search URLs to analyze: {len(google_urls)}")
    
    # Split into chunks based on token limits
    # Rough estimate: 1 token ≈ 4 characters, target ~150k tokens per batch (conservative for 200K limit)
    MAX_CHARS_PER_BATCH = 600000  # ~150k tokens
    batch_results = []
    
    # Split combined_text into chunks
    batch_num = 1
    start_idx = 0
    
    while start_idx < total_size:
        end_idx = min(start_idx + MAX_CHARS_PER_BATCH, total_size)
        batch_text = combined_text[start_idx:end_idx]
        
        # Try to split at a section boundary (double newline) to avoid cutting mid-review
        if end_idx < total_size and batch_text:
            # Look for the last section separator in this chunk
            last_section_sep = batch_text.rfind("\n\n")
            if last_section_sep > MAX_CHARS_PER_BATCH * 0.8:  # Only if we're not too close to start
                batch_text = batch_text[:last_section_sep]
                end_idx = start_idx + last_section_sep + 2
        
        batch_info = f"Batch {batch_num} (text chars {start_idx:,} to {end_idx:,} of {total_size:,})"
        
        # Google URLs section (only in first batch)
        urls_section = ""
        if google_urls and batch_num == 1:
            urls_list = "\n".join([f"- {url}" for url in google_urls])
            urls_section = f"""

GOOGLE SEARCH URLs TO ANALYZE (Visit these URLs using URL context):
{urls_list}
"""
        
        # Social search instruction (only in first batch)
        social_search = ""
        if product_name and batch_num == 1:
            social_search = f"""

SOCIAL MEDIA SEARCH:
Search for "{product_name} review" on relevant social media platforms (Twitter/X, Facebook, Instagram, Reddit, etc.).
Include findings from social media in your analysis.
"""
        
        prompt = f"""You are an expert app analyst. Analyze reviews and categorize findings into 7 types.

CRITICAL: Output ONLY in TOON (pipe-delimited) format. NO JSON, NO markdown.

TASKS:
1. Analyze all provided text data
2. {f'Visit and analyze the Google Search URLs using your URL context tool' if urls_section else 'Continue analysis'}
3. {f'Search social media for "{product_name} review" to gather additional user feedback' if social_search else 'Continue analysis'}
4. Categorize findings into: bug, feature_request, requirement, usability_friction, pain_point, positive_review, ai_insight
5. Generate AI insights by cross-referencing sources

OUTPUT FORMAT (TOON - pipe-delimited):
type | category | title | description | frequency | severity | sample_reviews | recommendation | priority_score | sources

FORMATTING RULES:
- Start with the header row exactly as shown above
- One finding per line
- Use semicolons (;) to separate multiple sample_reviews
- Use commas (,) to separate multiple sources
- Replace any pipe characters (|) in text fields with [PIPE]
- severity: critical, high, medium, or low
- priority_score: 1-10

{batch_info}
{batch_text}
{urls_section}
{social_search}

Output ONLY the TOON table (header + data rows). NO JSON, NO markdown, NO explanations."""
        
        try:
            # Create content with user prompt
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)]
                )
            ]
            
            loop = asyncio.get_event_loop()
            
            def generate_content():
                response_text = ""
                for chunk in client.models.generate_content_stream(
                    model=model_name,
                    contents=contents,
                    config=generate_config,
                ):
                    if hasattr(chunk, 'text') and chunk.text:
                        response_text += chunk.text
                return response_text
            
            response_text = await loop.run_in_executor(None, generate_content)
            response_text = response_text.strip()
            
            # Parse TOON format - extract findings as list for batch aggregation
            # We'll store raw TOON text and parse later during aggregation
            batch_result = {
                "toon_text": response_text,
                "batch_info": batch_info,
                "chars_processed": len(batch_text)
            }
            batch_results.append(batch_result)
            print(f"[Gemini] Processed {batch_info} ({len(batch_text):,} chars)")
            
            # Move to next batch
            start_idx = end_idx
            batch_num += 1
            
            # Rate limiting: Add delay between batches to avoid quota exhaustion
            # Free tier: 10 requests per minute, so wait 7 seconds between requests
            if start_idx < total_size:
                print(f"[Gemini] Waiting 7 seconds to avoid rate limit...")
                await asyncio.sleep(7)
                
        except Exception as e:
            print(f"[Gemini] Error processing batch {batch_num}: {e}")
            import traceback
            traceback.print_exc()
            # Skip this batch and continue
            start_idx = end_idx
            batch_num += 1
    
    # Aggregate batch results intelligently
    aggregated = _aggregate_batch_results(batch_results, scrape_results, data_summary)
    
    return aggregated


def _aggregate_batch_results(batch_results: list, scrape_results: list, data_summary: dict) -> dict:
    """
    Aggregate results from multiple batches into a unified analysis with 7-type categorization.
    
    Args:
        batch_results: List of batch analysis results
        scrape_results: List of tuples from scrape functions
        data_summary: Data summary dictionary
    
    Returns:
        Aggregated sentiment analysis dictionary with comprehensive categorization
    """
    print(f"[Gemini] Aggregating results from {len(batch_results)} batches...")
    
    # Combine all TOON text from batches
    combined_toon = []
    header_added = False
    
    for batch in batch_results:
        toon_text = batch.get("toon_text", "")
        lines = toon_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip header rows after the first one
            if 'type' in line.lower() and 'category' in line.lower() and 'title' in line.lower():
                if not header_added:
                    combined_toon.append(line)
                    header_added = True
                continue
            
            combined_toon.append(line)
    
    # Parse combined TOON
    combined_toon_text = '\n'.join(combined_toon)
    print(f"[Gemini] Combined TOON text: {len(combined_toon)} lines")
    
    analysis = _parse_toon_findings(combined_toon_text, scrape_results, data_summary)
    
    if analysis is None:
        # Fallback: return empty structure
        print(f"[Gemini] Warning: Failed to parse combined TOON. Returning empty structure.")
        return {
            "sources": [result[0] for result in scrape_results],
            "sentiment_analysis": {
                "overall_sentiment": {
                    "positive_percentage": 0,
                    "negative_percentage": 0,
                    "neutral_percentage": 0,
                    "average_rating": 0,
                    "total_reviews_analyzed": 0
                },
                "bugs": [],
                "feature_requests": [],
                "requirements": [],
                "usability_frictions": [],
                "pain_points": [],
                "positive_reviews": [],
                "ai_insights": [],
                "priority_actions": [],
                "key_insights": ["Failed to parse batch results"]
            },
            "data_summary": data_summary,
            "processing_mode": f"batch_processing ({len(batch_results)} batches) - parse failed"
        }
    
    return {
        "sources": [result[0] for result in scrape_results],
        "sentiment_analysis": analysis,
        "data_summary": data_summary,
        "processing_mode": f"batch_processing ({len(batch_results)} batches)"
    }


# ============================================================================
# Main Execution Function
# ============================================================================
async def main():
    """Main function to collect user inputs and execute scrapers conditionally."""
    
    print("=" * 60)
    print("Multi-Source Scraper with Sentiment Analysis")
    print("=" * 60)
    
    # Collect all user inputs upfront
    print("\n" + "=" * 60)
    print("PRODUCT INFORMATION")
    print("=" * 60)
    product_name = input("Enter product name (used for Reddit and Google Search): ").strip()
    
    print("\n" + "=" * 60)
    print("GOOGLE PLAY STORE (Optional)")
    print("=" * 60)
    google_product_id = input("Product ID (e.g., com.google.android.youtube) [press Enter to skip]: ").strip()
    google_platform = ""
    if google_product_id:
        google_platform = input("Platform (phone/tablet/tv/wearables/auto/chromebook) [default: phone]: ").strip().lower()
        if not google_platform:
            google_platform = "phone"
            print(f"Using default platform: {google_platform}")
    
    print("\n" + "=" * 60)
    print("APPLE APP STORE (Optional)")
    print("=" * 60)
    apple_product_id = input("Product ID (e.g., 544007664) [press Enter to skip]: ").strip()
    apple_country = ""
    if apple_product_id:
        country_input = input("Country (code like 'us' or name like 'United States') [default: us]: ").strip()
        if not country_input:
            country_input = "us"
        apple_country = get_country_code(country_input)
        print(f"Using country code: {apple_country}")
    
    # Configuration for URL batch processing
    print("\n" + "=" * 60)
    print("ADVANCED CONFIGURATION (Optional)")
    print("=" * 60)
    max_urls_per_batch = 20  # Default
    
    # Determine execution mode based on inputs
    tasks_to_run = []
    run_google_play = bool(google_product_id)
    run_apple = bool(apple_product_id)
    run_reddit = bool(product_name)
    run_google_search = bool(product_name)
    
    # Run conditionally
    if run_google_play:
        tasks_to_run.append(scrape_google_play_reviews(google_product_id, google_platform))
    
    if run_apple:
        tasks_to_run.append(scrape_apple_store_reviews(apple_product_id, apple_country))
    
    if run_reddit:
        tasks_to_run.append(scrape_reddit(product_name))
    
    if run_google_search:
        tasks_to_run.append(scrape_google_search(product_name))
    
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
    
    # Filter out errors and collect valid results (now tuples)
    scrape_results = []
    for result in results:
        if isinstance(result, Exception):
            print(f"Error in scraper: {result}")
            continue
        
        # Result is a tuple: (source, ..., data, total)
        # Google Play/Apple: 5 elements (source, id, platform/country, reviews, total)
        # Reddit/Google Search: 4 elements (source, keyword/query, urls/results, total)
        if result and len(result) >= 4:
            # Data is at index -2 (second to last), total is at index -1 (last)
            data = result[-2]
            if data:  # Check if there's data
                scrape_results.append(result)
    
    # Perform combined sentiment analysis on all results
    if scrape_results:
        print(f"\n{'=' * 60}")
        print(f"All {len(scrape_results)} scraper(s) completed.")
        print(f"{'=' * 60}")
        
        # Build combined query with metadata and TOON-formatted reviews
        print(f"\n{'=' * 60}")
        print("BUILDING COMBINED QUERY (METADATA + TOON)")
        print(f"{'=' * 60}")
        combined_query, data_summary = build_gemini_query(scrape_results)
        
        if combined_query:
            print(f"\n[TOON] Conversion successful!")
            print(f"[TOON] Combined query length: {len(combined_query):,} characters")
            print(f"[TOON] Estimated tokens: ~{len(combined_query) // 4:,} tokens")
            print(f"\n{'=' * 60}")
            print("COMBINED QUERY OUTPUT (METADATA + TOON):")
            print(f"{'=' * 60}")
            print(combined_query)
            print(f"{'=' * 60}")
            
            # Save TOON format to file
            toon_filename = "scraped_data.txt"
            with open(toon_filename, "w", encoding="utf-8") as f:
                f.write(combined_query)
            print(f"\nTOON format saved to {toon_filename}")
            
            # Display data summary
            if data_summary:
                print(f"\nData Summary:")
                for source, stats in data_summary.items():
                    source_name = source.replace("_", " ").title()
                    if "analyzed_reviews" in stats:
                        print(f"  {source_name}: {stats.get('analyzed_reviews', 0)} reviews")
                    elif "analyzed_items" in stats:
                        print(f"  {source_name}: {stats.get('analyzed_items', 0)} items")
        else:
            print("[TOON] Conversion failed or no data to convert")
        
        # Run Gemini API sentiment analysis (with product_name for social search)
        print(f"\nCombining results for sentiment analysis...")
        sentiment_result = await analyze_sentiment_with_gemini(
            combined_query, 
            data_summary, 
            scrape_results, 
            product_name,
            max_urls_per_batch
        )
        
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
                # Structured JSON output with 7-category display
                print("=" * 60)
                print("OVERALL SENTIMENT")
                print("=" * 60)
                overall = analysis.get("overall_sentiment", {})
                print(f"Positive: {overall.get('positive_percentage', 0):.1f}%")
                print(f"Negative: {overall.get('negative_percentage', 0):.1f}%")
                print(f"Neutral: {overall.get('neutral_percentage', 0):.1f}%")
                print(f"Average Rating: {overall.get('average_rating', 0):.2f}/5")
                print(f"Total Reviews Analyzed: {overall.get('total_reviews_analyzed', 0)}")
                
                # BUGS
                bugs = analysis.get("bugs", [])
                if bugs:
                    print(f"\n{'=' * 60}")
                    print(f"BUGS ({len(bugs)} found)")
                    print("=" * 60)
                    for i, bug in enumerate(bugs[:10], 1):  # Show top 10
                        print(f"\n{i}. [{bug.get('severity', 'N/A').upper()}] {bug.get('title', 'N/A')}")
                        print(f"   Category: {bug.get('category', 'N/A')}")
                        print(f"   Frequency: {bug.get('frequency', 0)} mentions | Priority: {bug.get('priority_score', 0)}/10")
                        print(f"   Sources: {', '.join(bug.get('sources', []))}")
                        if bug.get('recommendation'):
                            print(f"   Recommendation: {bug['recommendation']}")
                
                # FEATURE REQUESTS
                feature_requests = analysis.get("feature_requests", [])
                if feature_requests:
                    print(f"\n{'=' * 60}")
                    print(f"FEATURE REQUESTS ({len(feature_requests)} found)")
                    print("=" * 60)
                    for i, feat in enumerate(feature_requests[:10], 1):  # Show top 10
                        print(f"\n{i}. {feat.get('title', 'N/A')}")
                        print(f"   Category: {feat.get('category', 'N/A')}")
                        print(f"   Frequency: {feat.get('frequency', 0)} mentions | Priority: {feat.get('priority_score', 0)}/10")
                        print(f"   Sources: {', '.join(feat.get('sources', []))}")
                        if feat.get('recommendation'):
                            print(f"   Recommendation: {feat['recommendation']}")
                
                # REQUIREMENTS
                requirements = analysis.get("requirements", [])
                if requirements:
                    print(f"\n{'=' * 60}")
                    print(f"REQUIREMENTS ({len(requirements)} found)")
                    print("=" * 60)
                    for i, req in enumerate(requirements[:10], 1):  # Show top 10
                        print(f"\n{i}. {req.get('title', 'N/A')}")
                        print(f"   Category: {req.get('category', 'N/A')}")
                        print(f"   Frequency: {req.get('frequency', 0)} mentions | Priority: {req.get('priority_score', 0)}/10")
                        print(f"   Description: {req.get('description', 'N/A')[:200]}")
                        if req.get('recommendation'):
                            print(f"   Recommendation: {req['recommendation']}")
                
                # USABILITY FRICTIONS
                usability_frictions = analysis.get("usability_frictions", [])
                if usability_frictions:
                    print(f"\n{'=' * 60}")
                    print(f"USABILITY FRICTIONS ({len(usability_frictions)} found)")
                    print("=" * 60)
                    for i, ux in enumerate(usability_frictions[:10], 1):  # Show top 10
                        print(f"\n{i}. {ux.get('title', 'N/A')}")
                        print(f"   Category: {ux.get('category', 'N/A')}")
                        print(f"   Frequency: {ux.get('frequency', 0)} mentions | Severity: {ux.get('severity', 'N/A')}")
                        print(f"   Description: {ux.get('description', 'N/A')[:200]}")
                        if ux.get('recommendation'):
                            print(f"   Recommendation: {ux['recommendation']}")
                
                # PAIN POINTS
                pain_points = analysis.get("pain_points", [])
                if pain_points:
                    print(f"\n{'=' * 60}")
                    print(f"PAIN POINTS ({len(pain_points)} identified)")
                    print("=" * 60)
                    for i, pp in enumerate(pain_points[:10], 1):  # Show top 10
                        print(f"\n{i}. {pp.get('title', pp.get('issue', 'N/A'))}")
                        print(f"   Category: {pp.get('category', 'N/A')}")
                        print(f"   Frequency: {pp.get('frequency', 0)} mentions | Severity: {pp.get('severity', 'N/A')} | Priority: {pp.get('priority_score', 0)}/10")
                        if pp.get('recommendation'):
                            print(f"   Recommendation: {pp['recommendation']}")
                
                # POSITIVE REVIEWS
                positive_reviews = analysis.get("positive_reviews", [])
                if positive_reviews:
                    print(f"\n{'=' * 60}")
                    print(f"POSITIVE REVIEWS ({len(positive_reviews)} themes)")
                    print("=" * 60)
                    for i, pos in enumerate(positive_reviews[:10], 1):  # Show top 10
                        print(f"\n{i}. {pos.get('title', pos.get('theme', 'N/A'))}")
                        print(f"   Frequency: {pos.get('frequency', 0)} mentions")
                        print(f"   Description: {pos.get('description', 'N/A')[:200]}")
                        print(f"   Sources: {', '.join(pos.get('sources', []))}")
                
                # AI INSIGHTS
                ai_insights = analysis.get("ai_insights", [])
                if ai_insights:
                    print(f"\n{'=' * 60}")
                    print(f"AI INSIGHTS ({len(ai_insights)} generated)")
                    print("=" * 60)
                    for i, insight in enumerate(ai_insights, 1):
                        print(f"\n{i}. {insight.get('title', 'N/A')}")
                        print(f"   Type: {insight.get('category', 'pattern/correlation')}")
                        print(f"   Description: {insight.get('description', 'N/A')}")
                        if insight.get('sources'):
                            print(f"   Based on sources: {', '.join(insight['sources'])}")
                
                # Priority Actions
                priority_actions = analysis.get("priority_actions", [])
                if priority_actions:
                    print(f"\n{'=' * 60}")
                    print("PRIORITY ACTIONS")
                    print("=" * 60)
                    for i, action in enumerate(priority_actions[:7], 1):  # Show top 7
                        print(f"\n{i}. {action.get('action', 'N/A')}")
                        print(f"   Impact: {action.get('expected_impact', 'N/A')} | Effort: {action.get('effort_required', 'N/A')}")
                        print(f"   Reason: {action.get('reason', 'N/A')}")
                
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
