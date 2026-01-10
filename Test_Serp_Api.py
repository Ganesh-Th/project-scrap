import asyncio
import os
import time
import json
import random
import logging
from datetime import datetime
from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup
from google import genai as genai_new
from google.genai import types



# ============================================================================
# Logging Setup
# ============================================================================
def setup_logging():
    """Configures logging to both a file and the console."""
    log_filename = f"app_logs_{datetime.now().strftime('%Y%m%d')}.log"
    
    # Create logger
    logger = logging.getLogger("MultiSourceScraper")
    logger.setLevel(logging.INFO)

    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # File Handler (for persistence)
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()

# API Keys
SERPAPI_KEY = os.getenv('SERPAPI_KEY')
if not SERPAPI_KEY:
    logger.error("SERP API Keys missing from environment variables.")

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    logger.error("GEMINI API Keys missing from environment variables.")

# ============================================================================
# Helper Function: Create Gemini Client with URL Context and Google Search
# ============================================================================
def create_gemini_client_with_tools():
    """
    Create a new Gemini client with URL Context and Google Search capability.
    
    Returns:
        Tuple of (client, model_name, config)
    """
    logger.info("Initializing Gemini Client with Search tools...")
    
    try:
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

        logger.info("Gemini Client successfully configured.")
        return client, model_name, generate_config
    
    except Exception as e:
        logger.error(f"Failed to initialize Gemini Client: {str(e)}")
        raise

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
    logger.warning(f"Country mapping: '{user_input}' not found. Using as-is.")
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
    logger.info(f"[Google Play Store] Starting scrape for product: {product_id}, platform: {platform}")

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
        logger.debug(f"Sending request to SerpApi for Google Play product: {product_id}")
        search = GoogleSearch(params)
        results = search.get_dict()
        reviews = results.get("reviews", [])
        
        logger.info(f"[Google Play Store] Successfully fetched {len(reviews)} reviews")

        return (
            "google_play_store",
            product_id,
            platform,
            reviews,
            len(reviews)
        )
    except Exception as e:
        logger.error(f"[Google Play Store] Error scraping {product_id}: {e}", exc_info=True)
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
    logger.info(f"[Apple App Store] Starting scrape for product: {product_id}, country: {country}")

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
            
            logger.debug(f"[Apple App Store] Requesting page {page} for product {product_id}")

            search = GoogleSearch(params)
            results = search.get_dict()
            
            reviews = results.get("reviews", [])
            if not reviews:
                logger.warning(f"[Apple App Store] No reviews found on page {page}. Ending search.")
                break
            
            all_reviews.extend(reviews)
            logger.info(f"[Apple App Store] Fetched page {page}... Total reviews so far: {len(all_reviews)}")
            
            serpapi_pagination = results.get("serpapi_pagination", {})
            if "next" not in serpapi_pagination:
                logger.info("[Apple App Store] No more pages available.")
                break
            
            page += 1
        
        all_reviews = all_reviews[:target_reviews]
        
        logger.info(f"[Apple App Store] Successfully completed. Total fetched: {len(all_reviews)}")

        return (
            "apple_app_store",
            product_id,
            country,
            all_reviews,
            len(all_reviews)
        )
    except Exception as e:
        logger.error(f"[Apple App Store] Critical error during scrape of {product_id}: {e}", exc_info=True)
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
    logger.info(f"[Reddit] Visiting thread: {thread_url[:60]}...")
    
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
            logger.warning(f"[Reddit] Failed to load thread: {thread_url}. Status: {response.status_code}")
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
            logger.debug(f"[Reddit] Extracted {comment_count} comments from {title[:30]}...")

        return {
            "title": title,
            "posted": posted,
            "comment_count_stat": comment_count,
            "body_text": body_text,
            "comments_content": comments_data
        }

    except Exception as e:
        logger.error(f"[Reddit] Error reading thread {thread_url}: {e}", exc_info=True)
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
    logger.info(f"[Reddit] Starting keyword search for: {search_keyword}")
    
    base_url = "https://old.reddit.com/search"
    all_urls = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    logger.info(f"[Reddit] --- Starting search for: {search_keyword} ---")

    # Use relevance sort and filter by month
    current_url = f"{base_url}?q={search_keyword}&sort=relevance&t=month"
    
    page_counter = 0
    
    # Step 1: Collect URLs
    while current_url and page_counter < limit_pages:
            page_counter += 1
            logger.info(f"[Reddit] Scraping Search Page {page_counter}...")

            try:
                response = requests.get(current_url, headers=headers, timeout=10)
                
                # Handle rate limiting
                if response.status_code == 429:
                    logger.warning(f"[Reddit] Rate limit hit (429). Sleeping for 30 seconds... (Keyword: {search_keyword})")
                    await asyncio.sleep(30)
                    continue
                
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, "html.parser")
                
                results = soup.find_all("div", class_="search-result")
                
                if not results:
                    logger.info(f"[Reddit] No results found on page {page_counter}.")
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
                    logger.info(f"[Reddit] Reached end of search results at Page {page_counter}.")
                    current_url = None
            
            except Exception as e:
                logger.error(f"[Reddit] Error on search page {page_counter}: {e}", exc_info=True)
                break
    
    logger.info(f"[Reddit] Found {len(all_urls)} thread URLs. Beginning detail extraction...")

    # Step 2: Scrape full content from each URL
    session = requests.Session()
    scraped_posts = []
    
    for url in all_urls:
        post_data = scrape_reddit_thread_details(session, url)
        post_data["url"] = url  # Add URL for reference
        scraped_posts.append(post_data)
    
    total_posts = len(scraped_posts)
    logger.info(f"[Reddit] Successfully finished. Scraped {total_posts} threads for keyword: {search_keyword}")

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
    logger.info(f"[Google Search] Starting search for: {query}")

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY
    }
    
    try:
        logger.debug(f"Requesting Google Search results for query: {query}")
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
        
        logger.info(f"[Google Search] Successfully fetched {len(processed_results)} results")

        return (
            "google_search",
            query,
            processed_results,
            len(processed_results)
        )
    except Exception as e:
        logger.error(f"[Google Search] Error searching for {query}: {e}", exc_info=True)
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
        logger.warning(f"[TOON] Transformation skipped: No data for {source_type}")
        return ""
    
    logger.debug(f"[TOON] Converting {len(reviews)} items from {source_type} to TOON format")
    
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
    
    logger.info("[TOON Parser] Starting extraction of structured data from Gemini response...")
    
    # Schema: type | category | title | description | frequency | severity | sample_reviews | recommendation | priority_score | sources
    lines = toon_text.strip().split('\n')
    
    if not lines:
        logger.error("[TOON Parser] Failed: Gemini returned an empty text string.")
        return None
    
    # Find header line
    header_idx = -1
    for i, line in enumerate(lines):
        if 'type' in line.lower() and 'category' in line.lower() and 'title' in line.lower():
            header_idx = i
            break
    
    if header_idx == -1:
        logger.warning("[TOON Parser] No clear header found in AI response. Attempting to parse from line 0.")
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
            logger.warning(f"[TOON Parser] Skipping malformed row {line_num} (Insufficient columns): {line[:80]}...")
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
                sample_reviews = [
                    s.replace("[PIPE]", "|").replace("\"", "").replace('\\', '').strip()
                    for s in sample_reviews
                ]
            except json.JSONDecodeError:
                sample_reviews = [
                    s.replace("[PIPE]", "|").replace("\"", "").replace("\\", "").strip()
                    for s in sample_reviews_str.split(',') 
                    if s.strip()
                ]

            # Parse recommendation
            recommendation = parts[7] if len(parts) > 7 else ""
            recommendation = recommendation.replace('[PIPE]', '|').replace('"', '').replace('\\', '').strip()

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
            title = title.replace('[PIPE]', '|').replace('"', '').replace('\\', '').strip()

            description = description.replace('[PIPE]', '|').replace('"', '').replace('\\', '').strip()

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
            logger.error(f"[TOON Parser] Critical error parsing row {line_num}: {e}", exc_info=True)
            skipped_rows += 1
            continue
    
    logger.info(f"[TOON Parser] Parsing Summary: {len(findings)} findings captured, {skipped_rows} rows rejected.")

    if not findings:
        logger.error("[TOON Parser] Final result is empty. No valid findings were extracted from the text.")
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
        "summary_counts": {
            "bugs": len(bugs),
            "features": len(feature_requests),
            "requirements": len(requirements),
            "usability": len(usability_frictions),
            "pain_points": len(pain_points),
            "positive": len(positive_reviews),
            "ai_insights": len(ai_insights),
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
    
    logger.info(f"[TOON Parser] Successfully generated analysis: {len(findings)} total insights extracted.")
    
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
        logger.warning("[Query Builder] No scrape results provided. Query will be empty.")
        return "", {}
    
    logger.info(f"[Query Builder] Compiling data from {len(scrape_results)} sources for Gemini.")

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
    
    logger.info(f"[Query Builder] Query built successfully. Total size: {len(combined_query)} characters.")

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
    logger.info(f"[Gemini] Starting sentiment analysis for {len(sources)} sources.")

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
        logger.info(f"[Gemini] Estimated input tokens: ~{estimated_tokens}")

        # If data is too large, use batch processing
        MAX_TOKENS_PER_REQUEST = 200000
        
        if estimated_tokens > MAX_TOKENS_PER_REQUEST:
            logger.info(f"[Gemini] Large dataset detected. Using batch processing...")
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
        
        logger.info(f"[Gemini] Google Search URLs to analyze: {len(google_urls)}")
        
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
        
        logger.info(f"[Gemini] Sending request to {model_name}...")
        
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
        
        # Save raw TOON output to file
        with open("sentiment_analysis_toon.txt", "w", encoding="utf-8") as f:
            f.write(analysis_text)
        logger.info(f"[Gemini] Raw TOON output saved to sentiment_analysis_toon.txt")
        
        # Parse TOON format response
        analysis_json = _parse_toon_findings(analysis_text, scrape_results, data_summary)
        
        if analysis_json is not None:
            logger.info(f"[Gemini] Sentiment analysis completed for sources: {', '.join(sources)}")
            
            return {
                "sources": sources,
                "sentiment_analysis": analysis_json,
                "data_summary": data_summary,
                "processing_mode": "single_request"
            }
        
        # If parsing failed, return raw text for debugging
        logger.info(f"[Gemini] Warning: Could not parse TOON response.")
        logger.info(f"[Gemini] First 500 chars of response: {analysis_text[:500]}")
        return {
            "sources": sources,
            "sentiment_analysis": {"text": analysis_text},
            "data_summary": data_summary,
            "parse_error": "TOON parsing failed"
        }
    
    except Exception as e:
        logger.error(f"[Gemini] Critical failure: {e}", exc_info=True)
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
    logger.info(f"[Gemini] Processing large dataset in batches...")
    # Create Gemini client
    client, model_name, generate_config = create_gemini_client_with_tools()
    
    # Extract Google Search URLs (limit to 15 for first batch only)
    google_urls = extract_google_search_urls(scrape_results, max_urls=15)
    
    # Use TOON text directly
    combined_text = toon_text
    total_size = len(combined_text)
    logger.info(f"[Gemini] Total TOON text size: {total_size:,} characters (~{total_size // 4:,} tokens)")
    logger.info(f"[Gemini] Google Search URLs to analyze: {len(google_urls)}")
    
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
            logger.info(f"[Gemini] Processed {batch_info} ({len(batch_text):,} chars)")
            
            # Move to next batch
            start_idx = end_idx
            batch_num += 1
            
            # Rate limiting: Add delay between batches to avoid quota exhaustion
            # Free tier: 10 requests per minute, so wait 7 seconds between requests
            if start_idx < total_size:
                logger.info(f"[Gemini] Waiting 7 seconds to avoid rate limit...")
                await asyncio.sleep(7)
                
        except Exception as e:
            logger.error(f"[Gemini] Failed at batch {batch_num}: {e}")
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
    logger.info(f"[Gemini] Aggregating results from {len(batch_results)} batches...")
    
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
    logger.info(f"[Gemini] Combined TOON text: {len(combined_toon)} lines")
    
    # Save combined raw TOON output to file
    with open("sentiment_analysis_toon.txt", "w", encoding="utf-8") as f:
        f.write(combined_toon_text)
    logger.info(f"[Gemini] Raw TOON output saved to sentiment_analysis_toon.txt")
    
    analysis = _parse_toon_findings(combined_toon_text, scrape_results, data_summary)
    
    if analysis is None:
        # Fallback: return empty structure
        logger.warning(f"[Gemini] Warning: Failed to parse combined TOON. Returning empty structure.")
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
# Task 5: Task Prioritization (Lean / MoSCoW) - JSON OUTPUT
# ============================================================================
def clean_json_response(response_text: str) -> str:
    """Helper to extract JSON from response, removing markdown blocks and surrounding text."""
    # Remove markdown code blocks
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```").split("```")[1]
    
    # Now extract the JSON object from any remaining text
    # Find the first { and last }
    start_idx = response_text.find('{')
    end_idx = response_text.rfind('}')
    
    if start_idx != -1 and end_idx != -1:
        response_text = response_text[start_idx:end_idx + 1]
        
    return response_text.strip()


async def perform_prioritization(toon_content: str, method: str, duration: int, budget: int, business_goal: str) -> str:
    """
    Uses Gemini to prioritize tasks and returns a JSON string.
    """
    logger.info(f"Starting {method} prioritization. Goal: '{business_goal}', Budget: {budget}hrs")
    
    # Create Gemini client
    client, model_name, generate_config = create_gemini_client_with_tools()

    prompt = f"""You are an expert Product Manager.
    
    CONTEXT:
    We have analyzed user feedback and generated a list of issues (Bugs, Feature Requests, requirement, usability Friction, Pain point, postive review, ai_insight) in TOON format.
    We need to prioritize these tasks for our next sprint.

    INPUTS:
    1. PRIORITIZATION FRAMEWORK: {method}
       - If MoSCoW: Categorize into Must Have, Should Have, Could Have, Won't Have.
       - If Lean: Categorize into High Impact/Low Effort, High Impact/High Effort, Low Impact/Low Effort.
    2. SPRINT DURATION: {duration} Days
    3. RESOURCE BUDGET: {budget} Developer Hours
    4. CURRENT BUSINESS GOAL: "{business_goal}"

    INSTRUCTIONS:
    1. Analyze the TOON data provided below.
    2. Select the most critical items that align with the '{business_goal}' and {method}Framework.
    3. Estimate developer hours for each task based on severity and complexity (Make reasonable professional estimates).
    4. Ensure the total hours of selected 'Must Have' (or High Priority) tasks do not exceed the budget of {budget} hours.
    5. Output a structured plan.
    
    CRITICAL - OUTPUT FORMAT:
    - Do NOT include any explanation, reasoning, or text before the JSON
    - Do NOT include markdown code blocks (no ``json` or ```)
    - Output ONLY the raw JSON object starting with {{ and ending with }}
    - The response must be valid JSON that can be parsed by json.loads()
    
    JSON SCHEMA:
    {{
      "plan_metadata": {{
        "method": "{method}",
        "goal": "{business_goal}",
        "budget_hours": {budget},
        "sprint_duration_days": {duration}
      }},
      "prioritized_categories": [
        {{
          "category_name": "Name (e.g., Must Have or High Impact)",
          "tasks": [
            {{
              "title": "Task Title",
              "type": "bug/feature/etc",
              "impact_reasoning": "Why this is chosen",
              "estimated_hours": <int>
            }}
          ]
        }}
      ], 
      "summary": {{
        "total_estimated_hours": <int>,
        "budget_utilization_percentage": <float>,
        "key_risks": ["risk 1", "risk 2"]
      }}
    }}

    TOON DATA:
    {toon_content}
    """

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=generate_config
        )
        return clean_json_response(response.text)
    except Exception as e:
        # Return a valid JSON error structure so the main function doesn't crash
        return json.dumps({"error": f"Error during prioritization: {str(e)}"})


# ============================================================================
# Main Execution Function
# ============================================================================
async def main():
    """Main function to collect user inputs and execute scrapers conditionally."""
    
    logger.info("=" * 60)
    logger.info("Multi-Source Scraper with Sentiment Analysis")
    logger.info("=" * 60)
    
    # Collect all user inputs upfront
    logger.info("\n" + "=" * 60)
    logger.info("PRODUCT INFORMATION")
    logger.info("=" * 60)
    product_name = input("Enter product name (used for Reddit and Google Search): ").strip()
    logger.info({product_name})

    logger.info("\n" + "=" * 60)
    logger.info("GOOGLE PLAY STORE (Optional)")
    logger.info("=" * 60)
    google_product_id = input("Product ID (e.g., com.google.android.youtube) [press Enter to skip]: ").strip()
    logger.info({google_product_id})
    google_platform = ""
    if google_product_id:
        google_platform = input("Platform (phone/tablet/chromebook) [default: phone]: ").strip().lower()
        if not google_platform:
            google_platform = "phone"
            logger.info(f"Using default platform: {google_platform}")
    
    logger.info("\n" + "=" * 60)
    logger.info("APPLE APP STORE (Optional)")
    logger.info("=" * 60)
    apple_product_id = input("Product ID (e.g., 544007664) [press Enter to skip]: ").strip()
    logger.info(apple_product_id)
    apple_country = ""
    if apple_product_id:
        country_input = input("Country (code like 'us' or name like 'United States') [default: us]: ").strip()
        if not country_input:
            country_input = "us"
        apple_country = get_country_code(country_input)
        logger.info(f"Using country code: {apple_country}")
    
    # Configuration for URL batch processing
    logger.info("\n" + "=" * 60)
    logger.info("ADVANCED CONFIGURATION (Optional)")
    logger.info("=" * 60)
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
        logger.info("\nNo valid inputs provided. Exiting.")
        return
    
    # Execute scrapers (async if multiple, sync if single)
    logger.info(f"\n{'=' * 60}")
    logger.info(f"Executing {len(tasks_to_run)} scraper(s)...")
    logger.info(f"{'=' * 60}")
    
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
            logger.info(f"Error in scraper: {result}")
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
        logger.info(f"\n{'=' * 60}")
        logger.info(f"All {len(scrape_results)} scraper(s) completed.")
        logger.info(f"{'=' * 60}")
        
        # Build combined query with metadata and TOON-formatted reviews
        logger.info(f"\n{'=' * 60}")
        logger.info("BUILDING COMBINED QUERY (METADATA + TOON)")
        logger.info(f"{'=' * 60}")
        combined_query, data_summary = build_gemini_query(scrape_results)
        
        if combined_query:
            logger.info(f"\n[TOON] Conversion successful!")
            logger.info(f"[TOON] Combined query length: {len(combined_query):,} characters")
            logger.info(f"[TOON] Estimated tokens: ~{len(combined_query) // 4:,} tokens")
            logger.info(f"\n{'=' * 60}")
            logger.info("COMBINED QUERY OUTPUT (METADATA + TOON):")
            logger.info(f"{'=' * 60}")
            logger.info(combined_query)
            logger.info(f"{'=' * 60}")
            
            # Save TOON format to file
            toon_filename = "scraped_data.txt"
            with open(toon_filename, "w", encoding="utf-8") as f:
                f.write(combined_query)
            logger.info(f"\nINPUT DATA TOON format saved to {toon_filename}")
            
            # Display data summary
            if data_summary:
                logger.info(f"\nData Summary:")
                for source, stats in data_summary.items():
                    source_name = source.replace("_", " ").title()
                    if "analyzed_reviews" in stats:
                        logger.info(f"  {source_name}: {stats.get('analyzed_reviews', 0)} reviews")
                    elif "analyzed_items" in stats:
                        logger.info(f"  {source_name}: {stats.get('analyzed_items', 0)} items")
        else:
            logger.info("[TOON] Conversion failed or no data to convert")
        
        # Run Gemini API sentiment analysis (with product_name for social search)
        logger.info(f"\nCombining results for sentiment analysis...")
        sentiment_result = await analyze_sentiment_with_gemini(
            combined_query, 
            data_summary, 
            scrape_results, 
            product_name,
            max_urls_per_batch
        )
        
        # Display combined results
        logger.info(f"\n{'=' * 60}")
        logger.info("COMBINED SENTIMENT ANALYSIS RESULTS")
        logger.info(f"{'=' * 60}\n")
        
        if sentiment_result.get("error"):
            logger.info(f"Error in sentiment analysis: {sentiment_result['error']}\n")
        else:
            # Save to JSON file
            analysis_filename = "sentiment_analysis.json"
            with open(analysis_filename, "w", encoding="utf-8") as f:
                json.dump(sentiment_result, f, indent=2, ensure_ascii=False, separators=(',', ': '))
            
            logger.info(f"\n{'=' * 60}")
            logger.info(f"Analysis complete!")
            logger.info(f"Results saved to {analysis_filename} (structured JSON)")
            
            # ============================================================================
            # NEW ADDITION: Prioritization Step (JSON Output)
            # ============================================================================
            logger.info(f"\n{'=' * 60}")
            proceed = input("Do you want to proceed with Task Prioritization? (yes/no): ").strip().lower()
            
            if proceed in ['yes', 'y']:
                logger.info("\n--- Prioritization Configuration ---")
                
                logger.info("Select Prioritization Technique:")
                logger.info("1. Lean Prioritization (Value vs Effort)")
                logger.info("2. MoSCoW (Must, Should, Could, Won't)")
                method_choice = input("Enter choice (1 or 2): ").strip()
                method = "Lean Prioritization" if method_choice == "1" else "MoSCoW"
                
                try:
                    duration = int(input("Enter Sprint Duration (in days): ").strip())
                except ValueError:
                    duration = 14
                
                try:
                    budget = int(input("Enter Resource Budget (developer hours, e.g., 100): ").strip())
                except ValueError:
                    budget = 100 
                
                business_goal = input("Enter current Business Goal: ").strip()
                
                try:
                    # We need the TOON data from the file (or memory if you prefer)
                    with open("sentiment_analysis_toon.txt", "r", encoding="utf-8") as f:
                        toon_content = f.read()
                    
                    if not toon_content:
                        logger.error("Error: sentiment_analysis_toon.txt is empty.")
                    else:
                        # Get JSON String
                        plan_json_str = await perform_prioritization(toon_content, method, duration, budget, business_goal)
                        
                        try:
                            # Parse string to JSON object to ensure validity and allow pretty printing
                            plan_data = json.loads(plan_json_str)
                            
                            logger.info(f"\n{'=' * 60}")
                            logger.info("PRIORITIZATION PLAN (JSON)")
                            logger.info(f"{'=' * 60}\n")
                            
                            # Save to JSON file
                            output_file = "prioritization_plan.json"
                            with open(output_file, "w", encoding="utf-8") as f:
                                json.dump(plan_data, f, indent=2, ensure_ascii=False)
                            logger.info(f"\n[Saved prioritization plan to {output_file}]")

                        except json.JSONDecodeError as e:
                            logger.info("\n[Error] The AI response was not valid JSON. Saving raw response to prioritization_error.txt")
                            logger.info(f"[Error Details] {str(e)}")
                            with open("prioritization_error.txt", "w", encoding="utf-8") as f:
                                f.write(plan_json_str)

                except FileNotFoundError:
                    logger.info("Error: sentiment_analysis_toon.txt not found. Ensure analysis ran successfully.")
            else:
                logger.info("Prioritization was skipped.")
    else:
        logger.info("\nNo valid results to analyze.")
    
    logger.info(f"{'=' * 60}")
    logger.info("All tasks completed!")
    logger.info(f"{'=' * 60}")

if __name__ == "__main__":
    asyncio.run(main())
