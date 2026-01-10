"""Apple App Store scraper service."""
from serpapi import GoogleSearch

from app.config import get_settings
from app.logging_config import get_logger


logger = get_logger(__name__)
settings = get_settings()


async def scrape_apple_store_reviews(
    product_id: str, 
    country: str = "us", 
    target_reviews: int = 199
) -> tuple:
    """
    Scrape Apple App Store reviews.
    
    Args:
        product_id: Apple App Store product ID (e.g., 544007664)
        country: Country code (e.g., us, gb, ca)
        target_reviews: Target number of reviews to fetch (default: 199)
    
    Returns:
        tuple: (source, product_id, country, reviews_json, total_reviews)
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
                "api_key": settings.SERPAPI_KEY
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
