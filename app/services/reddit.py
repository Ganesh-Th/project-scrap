"""Async Reddit scraper service using httpx."""
import asyncio
import random
from typing import Dict, List, Any

import httpx
from bs4 import BeautifulSoup

from app.config import get_settings
from app.logging_config import get_logger
from app.utils.constants import USER_AGENTS


logger = get_logger(__name__)
settings = get_settings()


def _get_random_headers() -> Dict[str, str]:
    """Get random headers for request."""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }


async def _scrape_thread_details(
    client: httpx.AsyncClient, 
    thread_url: str,
    semaphore: asyncio.Semaphore
) -> Dict[str, Any]:
    """
    Visits a specific thread URL to extract the body text and comments.
    Uses semaphore for rate limiting.
    
    Args:
        client: httpx.AsyncClient instance
        thread_url: URL of the Reddit thread
        semaphore: asyncio.Semaphore for rate limiting
    
    Returns:
        dict with keys: title, posted, comment_count_stat, body_text, comments_content, url
    """
    async with semaphore:
        logger.info(f"[Reddit] Visiting thread: {thread_url[:60]}...")
        
        try:
            # Random sleep to avoid rate limiting
            await asyncio.sleep(random.uniform(2, 4))
            
            response = await client.get(
                thread_url,
                headers=_get_random_headers(),
                timeout=10.0
            )
            
            if response.status_code != 200:
                logger.warning(f"[Reddit] Failed to load thread: {thread_url}. Status: {response.status_code}")
                return {
                    "title": "[Error: Could not load]",
                    "posted": "Unknown",
                    "comment_count_stat": "0",
                    "body_text": "[Error: Could not load]",
                    "comments_content": [],
                    "url": thread_url
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
                    except Exception:
                        continue
                
                comment_count = str(len(comments_data))
                logger.debug(f"[Reddit] Extracted {comment_count} comments from {title[:30]}...")

            return {
                "title": title,
                "posted": posted,
                "comment_count_stat": comment_count,
                "body_text": body_text,
                "comments_content": comments_data,
                "url": thread_url
            }

        except Exception as e:
            logger.error(f"[Reddit] Error reading thread {thread_url}: {e}", exc_info=True)
            return {
                "title": "[Error]",
                "posted": "Unknown",
                "comment_count_stat": "0",
                "body_text": "[Error]",
                "comments_content": [],
                "url": thread_url
            }


async def scrape_reddit(keyword: str, limit_pages: int = 2) -> tuple:
    """
    Scrape Reddit using keyword search on old.reddit.com with full content extraction.
    Uses httpx.AsyncClient for async HTTP requests.
    
    Args:
        keyword: Single keyword to search for (will have " Review" appended)
        limit_pages: Maximum pages to scrape (default: 2)
    
    Returns:
        tuple: (source, keyword, scraped_posts_list, total_posts)
    """
    # Append " Review" to the keyword for Reddit search
    search_keyword = f"{keyword.strip()} Review"
    logger.info(f"[Reddit] Starting keyword search for: {search_keyword}")
    
    base_url = "https://old.reddit.com/search"
    all_urls: List[str] = []
    
    # Create async client with connection pooling
    async with httpx.AsyncClient(
        follow_redirects=True,
        limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
    ) as client:
        
        logger.info(f"[Reddit] --- Starting search for: {search_keyword} ---")

        # Use relevance sort and filter by month
        current_url = f"{base_url}?q={search_keyword}&sort=relevance&t=month"
        
        page_counter = 0
        
        # Step 1: Collect URLs
        while current_url and page_counter < limit_pages:
            page_counter += 1
            logger.info(f"[Reddit] Scraping Search Page {page_counter}...")

            try:
                response = await client.get(
                    current_url, 
                    headers=_get_random_headers(), 
                    timeout=10.0
                )
                
                # Handle rate limiting
                if response.status_code == 429:
                    logger.warning(f"[Reddit] Rate limit hit (429). Sleeping for 30 seconds...")
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

        # Step 2: Scrape full content from each URL concurrently with rate limiting
        # Use semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(settings.REDDIT_CONCURRENT_LIMIT)
        
        # Create tasks for concurrent scraping
        tasks = [
            _scrape_thread_details(client, url, semaphore) 
            for url in all_urls
        ]
        
        # Execute all tasks concurrently
        scraped_posts = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_posts = [
            post for post in scraped_posts 
            if isinstance(post, dict)
        ]
        
        total_posts = len(valid_posts)
        logger.info(f"[Reddit] Successfully finished. Scraped {total_posts} threads for keyword: {search_keyword}")

        return (
            "reddit",
            search_keyword,
            valid_posts,
            total_posts
        )
