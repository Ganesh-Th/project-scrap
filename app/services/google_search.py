"""Google Search scraper service."""
from serpapi import GoogleSearch

from app.config import get_settings
from app.logging_config import get_logger


logger = get_logger(__name__)
settings = get_settings()


async def scrape_google_search(product_name: str) -> tuple:
    """
    Scrape Google search results for product reviews using SerpAPI.
    
    Args:
        product_name: Name of the product to search for reviews
    
    Returns:
        tuple: (source, query, results_json, total_results)
    """
    query = f"{product_name} Review"
    logger.info(f"[Google Search] Starting search for: {query}")

    params = {
        "engine": "google",
        "q": query,
        "api_key": settings.SERPAPI_KEY
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
