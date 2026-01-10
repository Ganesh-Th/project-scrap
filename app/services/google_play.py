"""Google Play Store scraper service."""
from serpapi import GoogleSearch

from app.config import get_settings
from app.logging_config import get_logger


logger = get_logger(__name__)
settings = get_settings()


async def scrape_google_play_reviews(product_id: str, platform: str = "phone") -> tuple:
    """
    Scrape Google Play Store reviews.
    
    Args:
        product_id: Google Play Store product ID (e.g., com.google.android.youtube)
        platform: Platform type (phone/tablet/tv/wearables/auto/chromebook)
    
    Returns:
        tuple: (source, product_id, platform, reviews_json, total_reviews)
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
        "api_key": settings.SERPAPI_KEY
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
