"""Data processing utilities - TOON format conversion."""
import json
from typing import List, Dict, Any

from app.logging_config import get_logger
from app.utils.helpers import sanitize_pipe_text


logger = get_logger(__name__)


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
            snippet = sanitize_pipe_text(str(review.get("snippet", "")))
            row = f"{review.get('rating', '')} | {snippet} | {review.get('likes', '')} | {review.get('iso_date', '')}"
            rows.append(row)
        return "\n".join(rows)
    
    elif source_type == "apple_app_store":
        header = "title | text | rating | review_date | reviewed_version"
        rows = [header]
        for review in reviews:
            title = sanitize_pipe_text(str(review.get("title", "")))
            text = sanitize_pipe_text(str(review.get("text", "")))
            row = f"{title} | {text} | {review.get('rating', '')} | {review.get('review_date', '')} | {review.get('reviewed_version', '')}"
            rows.append(row)
        return "\n".join(rows)
    
    elif source_type == "reddit":
        header = "title | posted | comment_count_stat | body_text | comments_text"
        rows = [header]
        for post in reviews:
            title = sanitize_pipe_text(str(post.get("title", "")))
            posted = sanitize_pipe_text(str(post.get("posted", "")))
            comment_count = sanitize_pipe_text(str(post.get("comment_count_stat", "")))
            body_text = sanitize_pipe_text(str(post.get("body_text", "")))
            
            # Extract only text field from comments_content
            comments_texts = [
                sanitize_pipe_text(str(c.get("text", "")))
                for c in post.get("comments_content", [])
            ]
            comments_combined = " | ".join(comments_texts) if comments_texts else ""
            
            row = f"{title} | {posted} | {comment_count} | {body_text} | {comments_combined}"
            rows.append(row)
        return "\n".join(rows)
    
    elif source_type == "google_search":
        header = "link | snippet | source | rich_snippet | sitelinks"
        rows = [header]
        for result in reviews:
            snippet = sanitize_pipe_text(str(result.get("snippet", "")))
            
            # Convert nested structures to JSON strings
            rich_snippet_str = json.dumps(result.get("rich_snippet")) if "rich_snippet" in result else ""
            sitelinks_str = json.dumps(result.get("sitelinks")) if "sitelinks" in result else ""
            
            row = f"{result.get('link', '')} | {snippet} | {result.get('source', '')} | {rich_snippet_str} | {sitelinks_str}"
            rows.append(row)
        return "\n".join(rows)
    
    return ""


def build_gemini_query(scrape_results: list) -> tuple:
    """
    Build the combined query string for Gemini API.
    Combines metadata and TOON-formatted reviews from all sources.
    
    Args:
        scrape_results: List of tuples from scrape functions
    
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
            _, keyword, posts, total_posts = result
            posts_toon = convert_reviews_to_toon(posts, "reddit")
            
            section = f"""=== REDDIT POSTS ===
Source: {source}
Keyword: {keyword}
Total Posts: {total_posts}

Posts (TOON format):
{posts_toon}"""
            sections.append(section)
            
            data_summary[source] = {
                "total_posts": total_posts,
                "analyzed_items": total_posts
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


def extract_google_search_urls(scrape_results: list, max_urls: int = 15) -> List[str]:
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


def parse_toon_findings(toon_text: str, scrape_results: list, data_summary: dict) -> Dict[str, Any]:
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
        
        if len(parts) < 3:
            logger.warning(f"[TOON Parser] Skipping malformed row {line_num} (Insufficient columns)")
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
            
            # Parse sample_reviews
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
            
            # Parse sources
            sources_str = parts[9] if len(parts) > 9 else ""
            sources = [s.strip() for s in sources_str.split(',') if s.strip()]
            
            # Clean text fields
            title = title.replace('[PIPE]', '|').replace('"', '').replace('\\', '').strip()
            description = description.replace('[PIPE]', '|').replace('"', '').replace('\\', '').strip()

            finding = {
                "type": finding_type.strip(),
                "category": category,
                "title": title,
                "description": description,
                "frequency": frequency,
                "severity": severity,
                "sample_reviews": sample_reviews[:3],
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
        logger.error("[TOON Parser] Final result is empty. No valid findings were extracted.")
        return None
    
    # Group findings by type
    bugs = [f for f in findings if f["type"] == "bug"]
    feature_requests = [f for f in findings if f["type"] == "feature_request"]
    requirements = [f for f in findings if f["type"] == "requirement"]
    usability_frictions = [f for f in findings if f["type"] == "usability_friction"]
    pain_points = [f for f in findings if f["type"] == "pain_point"]
    positive_reviews = [f for f in findings if f["type"] == "positive_review"]
    ai_insights = [f for f in findings if f["type"] == "ai_insight"]
    
    # Calculate overall sentiment
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
    
    # Calculate average rating
    ratings = []
    for result in scrape_results:
        source = result[0]
        if source in ["google_play_store", "apple_app_store"]:
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
    
    # Build priority actions
    priority_actions = []
    
    critical_bugs = sorted([f for f in bugs if f["severity"] == "critical"], 
                          key=lambda x: x["priority_score"], reverse=True)[:3]
    for bug in critical_bugs:
        priority_actions.append({
            "action": f"Fix critical bug: {bug['title']}",
            "reason": f"Critical severity with {bug['frequency']} mentions",
            "expected_impact": "high",
            "effort_required": "high"
        })
    
    top_requirements = sorted(requirements, key=lambda x: x["priority_score"], reverse=True)[:2]
    for req in top_requirements:
        priority_actions.append({
            "action": f"Implement required feature: {req['title']}",
            "reason": f"Expected by users ({req['frequency']} mentions)",
            "expected_impact": "high",
            "effort_required": "medium"
        })
    
    top_frictions = sorted(usability_frictions, key=lambda x: x["priority_score"], reverse=True)[:2]
    for friction in top_frictions:
        priority_actions.append({
            "action": f"Fix UX issue: {friction['title']}",
            "reason": f"Causes user frustration ({friction['frequency']} mentions)",
            "expected_impact": "medium",
            "effort_required": "low"
        })
    
    priority_actions = priority_actions[:7]
    
    # Build key insights
    key_insights = []
    
    if bugs:
        key_insights.append(f"Found {len(bugs)} bugs, {len(critical_bugs)} critical. Top issue: {bugs[0]['title']}")
    
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
