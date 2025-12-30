
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

