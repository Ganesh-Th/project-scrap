"""Gemini sentiment analysis service."""
import asyncio
from typing import Dict, Any

from google import genai as genai_new
from google.genai import types

from app.config import get_settings
from app.logging_config import get_logger
from app.services.data_processor import (
    extract_google_search_urls,
    parse_toon_findings
)


logger = get_logger(__name__)
settings = get_settings()


def create_gemini_client_with_tools():
    """
    Create a new Gemini client with URL Context and Google Search capability.
    
    Returns:
        Tuple of (client, model_name, config)
    """
    logger.info("Initializing Gemini Client with Search tools...")
    
    try:
        client = genai_new.Client(api_key=settings.GEMINI_API_KEY)
        model_name = "gemini-2.5-flash-lite"
        
        tools = [
            types.Tool(url_context=types.UrlContext()),
            types.Tool(googleSearch=types.GoogleSearch()),
        ]
        
        generate_config = types.GenerateContentConfig(
            tools=tools,
        )

        logger.info("Gemini Client successfully configured.")
        return client, model_name, generate_config
    
    except Exception as e:
        logger.error(f"Failed to initialize Gemini Client: {str(e)}")
        raise


async def analyze_sentiment_with_gemini(
    combined_query: str, 
    data_summary: dict, 
    scrape_results: list, 
    product_name: str = ""
) -> Dict[str, Any]:
    """
    Analyze sentiment of combined scraped data using Gemini API.
    
    Args:
        combined_query: Combined query string with metadata and TOON-formatted reviews
        data_summary: Dictionary containing summary of data from each source
        scrape_results: List of tuples from scrape functions
        product_name: Product name for social media search
    
    Returns:
        Dictionary containing comprehensive sentiment analysis
    """
    sources = [result[0] for result in scrape_results if result]
    logger.info(f"[Gemini] Starting sentiment analysis for {len(sources)} sources.")

    try:
        client, model_name, generate_config = create_gemini_client_with_tools()
        
        if not combined_query:
            return {
                "error": "No text data to analyze from any source",
                "sources": sources
            }
        
        combined_text = combined_query
        estimated_tokens = len(combined_text) // 4
        logger.info(f"[Gemini] Estimated input tokens: ~{estimated_tokens}")

        MAX_TOKENS_PER_REQUEST = 200000
        
        if estimated_tokens > MAX_TOKENS_PER_REQUEST:
            logger.info(f"[Gemini] Large dataset detected. Using batch processing...")
            return await _analyze_sentiment_batch_processing(
                model_name, scrape_results, combined_text, data_summary, product_name
            )
        
        google_urls = extract_google_search_urls(scrape_results, max_urls=15)
        
        urls_section = ""
        if google_urls:
            urls_list = "\n".join([f"- {url}" for url in google_urls])
            urls_section = f"""

GOOGLE SEARCH URLs TO ANALYZE (Visit these URLs using URL context and extract review content):
{urls_list}
"""
        
        social_search_instruction = ""
        if product_name:
            social_search_instruction = f"""

SOCIAL MEDIA SEARCH:
Search for "{product_name} review" on relevant social media platforms.
Include findings from social media in your analysis.
"""
        
        logger.info(f"[Gemini] Google Search URLs to analyze: {len(google_urls)}")
        
        prompt = _build_analysis_prompt(combined_text, urls_section, social_search_instruction, product_name)
        
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )
        ]
        
        logger.info(f"[Gemini] Sending request to {model_name}...")
        
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
        analysis_json = parse_toon_findings(analysis_text, scrape_results, data_summary)
        
        if analysis_json is not None:
            logger.info(f"[Gemini] Sentiment analysis completed for sources: {', '.join(sources)}")
            
            return {
                "sources": sources,
                "sentiment_analysis": analysis_json,
                "data_summary": data_summary,
                "processing_mode": "single_request",
                "toon_text": analysis_text
            }
        
        logger.warning(f"[Gemini] Could not parse TOON response.")
        return {
            "sources": sources,
            "sentiment_analysis": {"text": analysis_text},
            "data_summary": data_summary,
            "parse_error": "TOON parsing failed",
            "toon_text": analysis_text
        }
    
    except Exception as e:
        logger.error(f"[Gemini] Critical failure: {e}", exc_info=True)
        return {
            "error": str(e),
            "sources": sources if 'sources' in dir() else []
        }


async def _analyze_sentiment_batch_processing(
    model_name: str, 
    scrape_results: list, 
    toon_text: str, 
    data_summary: dict, 
    product_name: str = ""
) -> Dict[str, Any]:
    """Handle large datasets by processing in batches."""
    logger.info(f"[Gemini] Processing large dataset in batches...")
    
    client, model_name, generate_config = create_gemini_client_with_tools()
    google_urls = extract_google_search_urls(scrape_results, max_urls=15)
    
    combined_text = toon_text
    total_size = len(combined_text)
    logger.info(f"[Gemini] Total TOON text size: {total_size:,} characters (~{total_size // 4:,} tokens)")
    
    MAX_CHARS_PER_BATCH = 600000
    batch_results = []
    
    batch_num = 1
    start_idx = 0
    
    while start_idx < total_size:
        end_idx = min(start_idx + MAX_CHARS_PER_BATCH, total_size)
        batch_text = combined_text[start_idx:end_idx]
        
        if end_idx < total_size and batch_text:
            last_section_sep = batch_text.rfind("\n\n")
            if last_section_sep > MAX_CHARS_PER_BATCH * 0.8:
                batch_text = batch_text[:last_section_sep]
                end_idx = start_idx + last_section_sep + 2
        
        batch_info = f"Batch {batch_num} (text chars {start_idx:,} to {end_idx:,} of {total_size:,})"
        
        urls_section = ""
        if google_urls and batch_num == 1:
            urls_list = "\n".join([f"- {url}" for url in google_urls])
            urls_section = f"""

GOOGLE SEARCH URLs TO ANALYZE (Visit these URLs using URL context):
{urls_list}
"""
        
        social_search = ""
        if product_name and batch_num == 1:
            social_search = f"""

SOCIAL MEDIA SEARCH:
Search for "{product_name} review" on relevant social media platforms.
Include findings from social media in your analysis.
"""
        
        prompt = _build_batch_prompt(batch_text, urls_section, social_search, product_name, batch_info)
        
        try:
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
            
            batch_result = {
                "toon_text": response_text,
                "batch_info": batch_info,
                "chars_processed": len(batch_text)
            }
            batch_results.append(batch_result)
            logger.info(f"[Gemini] Processed {batch_info} ({len(batch_text):,} chars)")
            
            start_idx = end_idx
            batch_num += 1
            
            if start_idx < total_size:
                logger.info(f"[Gemini] Waiting 7 seconds to avoid rate limit...")
                await asyncio.sleep(7)
                
        except Exception as e:
            logger.error(f"[Gemini] Failed at batch {batch_num}: {e}")
            start_idx = end_idx
            batch_num += 1
    
    aggregated = _aggregate_batch_results(batch_results, scrape_results, data_summary)
    return aggregated


def _aggregate_batch_results(
    batch_results: list, 
    scrape_results: list, 
    data_summary: dict
) -> Dict[str, Any]:
    """Aggregate results from multiple batches."""
    logger.info(f"[Gemini] Aggregating results from {len(batch_results)} batches...")
    
    combined_toon = []
    header_added = False
    
    for batch in batch_results:
        toon_text = batch.get("toon_text", "")
        lines = toon_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if 'type' in line.lower() and 'category' in line.lower() and 'title' in line.lower():
                if not header_added:
                    combined_toon.append(line)
                    header_added = True
                continue
            
            combined_toon.append(line)
    
    combined_toon_text = '\n'.join(combined_toon)
    logger.info(f"[Gemini] Combined TOON text: {len(combined_toon)} lines")
    
    analysis = parse_toon_findings(combined_toon_text, scrape_results, data_summary)
    
    if analysis is None:
        logger.warning(f"[Gemini] Failed to parse combined TOON. Returning empty structure.")
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
            "processing_mode": f"batch_processing ({len(batch_results)} batches) - parse failed",
            "toon_text": combined_toon_text
        }
    
    return {
        "sources": [result[0] for result in scrape_results],
        "sentiment_analysis": analysis,
        "data_summary": data_summary,
        "processing_mode": f"batch_processing ({len(batch_results)} batches)",
        "toon_text": combined_toon_text
    }


def _build_analysis_prompt(
    combined_text: str, 
    urls_section: str, 
    social_search_instruction: str, 
    product_name: str
) -> str:
    """Build the main analysis prompt."""
    return f"""You are an expert app analyst specializing in user feedback analysis.

CRITICAL: Output ONLY in TOON (pipe-delimited) format. NO JSON, NO markdown, just the TOON table.

TASKS:
1. Analyze ALL reviews and discussions from all provided sources
2. Visit and analyze the Google Search URLs using your URL context tool to extract full review content
3. {f'Search social media for "{product_name} review" to gather additional user feedback' if product_name else 'Use only the provided data'}
4. Categorize EVERY finding into exactly ONE of these 7 types:
   - bug: Technical issues, crashes, errors, broken features
   - feature_request: User-requested new features or enhancements
   - requirement: Must-have features users expect but are missing
   - usability_friction: UX issues that frustrate users
   - pain_point: General problems causing user dissatisfaction
   - positive_review: Things users love, praise, and appreciate
   - ai_insight: Patterns, trends, or correlations YOU identify
5. Generate AI insights by finding hidden patterns and correlations

OUTPUT FORMAT (TOON - pipe-delimited):
type | category | title | description | frequency | severity | sample_reviews | recommendation | priority_score | sources

FORMATTING RULES:
- Start with the header row exactly as shown above
- One finding per line
- Use semicolons (;) to separate multiple sample_reviews
- Use commas (,) to separate multiple sources
- Replace any pipe characters (|) in text fields with [PIPE]
- severity: critical, high, medium, or low
- priority_score: 1-10, higher = more urgent
- sources: reddit, google_play_store, apple_app_store, google_search, or social_media

SCRAPED DATA FROM ALL SOURCES (TOON format):
{combined_text}
{urls_section}
{social_search_instruction}

Remember: Output ONLY the TOON table (header + data rows). NO JSON, NO markdown."""


def _build_batch_prompt(
    batch_text: str, 
    urls_section: str, 
    social_search: str, 
    product_name: str, 
    batch_info: str
) -> str:
    """Build the batch analysis prompt."""
    return f"""You are an expert app analyst. Analyze reviews and categorize findings into 7 types.

CRITICAL: Output ONLY in TOON (pipe-delimited) format. NO JSON, NO markdown.

TASKS:
1. Analyze all provided text data
2. {f'Visit and analyze the Google Search URLs using your URL context tool' if urls_section else 'Continue analysis'}
3. {f'Search social media for "{product_name} review"' if social_search else 'Continue analysis'}
4. Categorize findings into: bug, feature_request, requirement, usability_friction, pain_point, positive_review, ai_insight
5. Generate AI insights by cross-referencing sources

OUTPUT FORMAT (TOON - pipe-delimited):
type | category | title | description | frequency | severity | sample_reviews | recommendation | priority_score | sources

FORMATTING RULES:
- Start with the header row exactly as shown above
- One finding per line
- severity: critical, high, medium, or low
- priority_score: 1-10

{batch_info}
{batch_text}
{urls_section}
{social_search}

Output ONLY the TOON table (header + data rows). NO JSON, NO markdown, NO explanations."""
