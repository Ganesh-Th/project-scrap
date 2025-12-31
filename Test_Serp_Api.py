
### Google Play Store Reviews working  ###
# from serpapi import GoogleSearch
# import json
# import os

# API_KEY = os.getenv('SERPAPI_KEY')
# if not API_KEY:
#     raise RuntimeError("SERPAPI_KEY not set")

# params = {
#   "engine": "google_play_product",
#   "store": "apps",
#   "product_id": "com.google.android.youtube",
#   "all_reviews": "true",
#   "platform": "phone",
#   "sort_by": "2",
#   "num": "199",
#   "json_restrictor": "reviews[].{id, rating, snippet, likes, iso_date}",
#   "api_key": API_KEY
# }

# search = GoogleSearch(params)
# results = search.get_dict()

# reviews = results["reviews"]
# with open("Google_reviews.json", "w", encoding="utf-8") as f:
#     json.dump(reviews, f, ensure_ascii=False, indent=2)

# print("Saved reviews to Google_reviews.json")



### App store working  ###
# from serpapi import GoogleSearch
# import json
# import os

# API_KEY = os.getenv('SERPAPI_KEY')
# if not API_KEY:
#      raise RuntimeError("SERPAPI_KEY not set")

# PRODUCT_ID = "544007664"
# TARGET_REVIEWS = 199

# all_reviews = []
# page = 1

# while len(all_reviews) < TARGET_REVIEWS:
#     params = {
#         "engine": "apple_reviews",
#         "product_id": PRODUCT_ID,
#         "country": "us",
#         "page": page,
#         "json_restrictor": "reviews[].{id, title, text, rating, review_date, reviewed_version}, serpapi_pagination",
#         "api_key": API_KEY
#     }

#     search = GoogleSearch(params)
#     results = search.get_dict()

#     reviews = results.get("reviews", [])
#     if not reviews:
#         break

#     all_reviews.extend(reviews)
#     print(f"Fetched page {page}... Total reviews so far: {len(all_reviews)}")


#     serpapi_pagination = results.get("serpapi_pagination", {})
#     if "next" not in serpapi_pagination:
#         break

#     page += 1

# all_reviews = all_reviews[:TARGET_REVIEWS]

# with open("apple_reviews.json", "w", encoding="utf-8") as f:
#     json.dump(all_reviews, f, ensure_ascii=False, indent=2)

# print(f"Successfully saved {len(all_reviews)} reviews to apple_reviews.json")



### Reddit Scrapping working  ###
# import requests
# import json
# import time
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin

# def scrape_reddit(topic: str, keywords: list) -> list[dict]:
#     base_reddit_url = "https://www.reddit.com"
#     subreddits = [
#         f"https://www.reddit.com/r/{topic}", #   
#         f"https://www.reddit.com/r/{topic}/hot"  # /hot gives you a trending result
#     ]

#     all_data = []
#     for url in subreddits:
#         headers ={
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
#         }

#         subreddit_name = url.split("/")[-1]
#         print(f'Scraping for: {subreddit_name}')

#         try:
#             response = requests.get(url, headers=headers, timeout=10)
#             response. raise_for_status()

#             soup = BeautifulSoup(response. content, "html.parser")

#             subreddit_data ={
#                 "subreddit_name" : subreddit_name,
#                 "url" : url,
#                 "title": soup. title.string if soup. title else "No title",
#                 "scraped_at" : time.strftime("%Y-4m-%d %H:%M:%S")
#             }

#             topics = []
#             for heading in soup.find_all(["h1","h2","h3","h4"]):
#                 text = heading.get_text(strip=True)

#                 if text and len(text) > 3:
#                     if any(k in text. lower() for k in keywords): 
#                         topics.append({
#                             "title":text,
#                             "type": f"{topic}_topic"
#                         })

#             discussions = []
#             seen_urls = set()
            
#             for link in soup. find_all("a", href=True):
#                 text = link.get_text(strip=True)
#                 href = link["href"]

#                 if text and len(text) > 1 and "/comments/" in href and href not in seen_urls:
#                     seen_urls.add(href)

#                 full_url = urljoin(base_reddit_url, href) # FIX: Handle relative links (/r/...) vs absolute links (https://...)

#                 discussions.append({
#                     "title": text[:100] +" ... " if len(text) > 100 else text,
#                     "url":full_url,
#                     "type":"discussion"
#                 })

#             subreddit_data["found_topics"] = topics
#             subreddit_data["discussions"] = discussions

#             all_data.append(subreddit_data)
#             time.sleep(2)
        
#         except Exception as e:
#             print(f'Error: {e}')
    
#     return all_data

# def save_scraped_data(data, filename_json="reddit.json"):
#     if not data:
#         print(f'No data')

#     try:
#         with open(filename_json, "w", encoding="utf-8") as file:
#             json.dump(data, file, indent=2, ensure_ascii=True)
#             print(f'{filename_json} is saved')
#     except Exception as e:
#         print("ERROR:",e)


# def main() -> None:
#     user_topic = input("Enter the Subreddit name (e.g., Python, Gaming, Tech): ").strip()
#     user_keywords = input("Enter keywords to filter for, separated by commas: ").split(",")
    
#    # Clean up whitespace from keywords
#     user_keywords = [k.strip() for k in user_keywords if k.strip()]
    
#    # If user provides no keywords, use the topic name as the default keyword
#     if not user_keywords:
#         user_keywords = [user_topic]

#     print(f"\nSearching for '{user_topic}' with filters: {user_keywords}...")
    
#     data = scrape_reddit(user_topic, user_keywords)
    
#     if data:
#         print(f'Processing the data ... ')
#         total_topics = 0
#         total_discussions = 0

#         for subreddit_data in data:
#             topics_count = len(subreddit_data.get("found_topics", []))
#             discussions_count = len(subreddit_data.get("discussions", []))

#             total_topics += topics_count
#             total_discussions += discussions_count

#         print(f'\nTotal: {total_topics} Python Topics, {discussions_count} Discussions')

#         save_scraped_data(data)
#     else:
#         print("There is not data returned!")

# if __name__ == "__main__":
#    main()




###  Reddit using keyword (But only 50 Threads)###
# import requests
# import json
# import time
# from bs4 import BeautifulSoup

# def scrape_reddit_search(keywords: list, limit_pages=50) -> list[dict]:
#     # 1. Use old.reddit.com for easier HTML parsing , beacuse new one is made of next.js/react not possible to scrape
#     base_url = "https://old.reddit.com/search"
    
#     all_data = []

#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#     }

#     for keyword in keywords:
#         keyword = keyword.strip()
#         if not keyword:
#             continue

#         print(f'--- Starting search for: "{keyword}" ---')

#         # FIX 1: Change sort to 'new'. 
#         # 'relevance' sometimes hides older results or breaks pagination on old.reddit.
#         current_url = f"{base_url}?q={keyword}&sort=relevance&t=month"
        
#         keyword_results = []
#         page_counter = 0

#         while current_url and page_counter < limit_pages:
#             page_counter += 1
#             print(f"   Scraping Page {page_counter}...")

#             try:
#                 response = requests.get(current_url, headers=headers, timeout=10)
                
#                 if response.status_code == 429:
#                     print("   !!! Rate limit hit (429). Sleeping for 30 seconds...")
#                     time.sleep(30)
#                     continue 
                
#                 response.raise_for_status()

#                 soup = BeautifulSoup(response.content, "html.parser")
                
#                 results = soup.find_all("div", class_="search-result")
                
#                 if not results:
#                     print("   No results found on this page.")
#                     break

#                 for result in results:
#                     title_tag = result.find("a", class_="search-title")
#                     sub_tag = result.find("a", class_="search-subreddit-link")
#                     comments_tag = result.find("a", class_="search-comments")
#                     time_tag = result.find("span", class_="search-time")

#                     if title_tag:
#                         title = title_tag.get_text(strip=True)
#                         href = title_tag["href"]
                        
#                         if href.startswith("/"):
#                             href = f"https://old.reddit.com{href}"

#                         post_data = {
#                             "title": title,
#                             "url": href,
#                             "subreddit": sub_tag.get_text(strip=True) if sub_tag else "Unknown",
#                             "comments": comments_tag.get_text(strip=True) if comments_tag else "0 comments",
#                             "posted": time_tag.get_text(strip=True) if time_tag else "Unknown"
#                         }
#                         keyword_results.append(post_data)

#                 # --- PAGINATION LOGIC (FIXED) ---
#                 next_button = soup.find("span", class_="nextprev")
#                 next_link = None
                
#                 if next_button:
#                     for link in next_button.find_all("a"):
#                         # Check if text contains 'next'
#                         if "next" in link.get_text(strip=True).lower():
#                             next_link = link["href"]
#                             break
                
#                 if next_link:
#                     # FIX 2: Handle Relative URLs
#                     # Sometimes Reddit returns "/search?q=..." instead of "https://..."
#                     if next_link.startswith("/"):
#                         next_link = f"https://old.reddit.com{next_link}"
                    
#                     current_url = next_link
#                     time.sleep(2) 
#                 else:
#                     print(f"   Reached last page (No 'Next' button found on Page {page_counter}).")
#                     current_url = None

#             except Exception as e:
#                 print(f'   Error on page {page_counter}: {e}')
#                 break
        
#         all_data.append({
#             "keyword": keyword,
#             "total_found": len(keyword_results),
#             "results": keyword_results
#         })

#     return all_data

# def save_scraped_data(data, filename_json="reddit.json"):
#     if not data:
#         print('No data to save.')
#         return

#     try:
#         with open(filename_json, "w", encoding="utf-8") as file:
#             json.dump(data, file, indent=2, ensure_ascii=True)
#             print(f'\nSuccess! Data saved to {filename_json}')
#     except Exception as e:
#         print("ERROR saving file:", e)

# def main() -> None:
#     user_input = input("Enter keywords (comma separated): ").strip()
    
#     if not user_input:
#         return

#     user_keywords = [k.strip() for k in user_input.split(",") if k.strip()]
    
#     # I increased the limit to 50 pages. 
#     # If a keyword has 1000s of results, this will scrape 50 * 25 = 1250 threads.
#     data = scrape_reddit_search(user_keywords, limit_pages=50)
    
#     if data:
#         total_threads = sum(item["total_found"] for item in data)
#         print(f'\nDone! Extracted {total_threads} threads total.')
#         save_scraped_data(data)
#     else:
#         print("No data returned!")

# if __name__ == "__main__":
#     main()



### Google search working ###

# from serpapi import GoogleSearch
# import json
# import os

# API_KEY = os.getenv('SERPAPI_KEY')
# if not API_KEY:
#     raise RuntimeError("SERPAPI_KEY not set")

# g_search = input("Enter the Product name: ")
# full = f"{g_search}"+ " "+"Review" 

# params = {
#   "engine": "google",
#   "q": full,
#   "api_key": API_KEY
# }

# search = GoogleSearch(params)
# results = search.get_dict()

# organic_results = results["organic_results"]

# with open("Google_search.json", "w", encoding="utf-8") as f:
#     json.dump(organic_results, f, ensure_ascii=False, indent=2)

# print("Saved reviews to Google_search.json")
