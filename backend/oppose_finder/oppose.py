import requests
from urllib.parse import unquote
from sentence_transformers import SentenceTransformer, util
from ..news_summarizer import article_scraper

SERP_API_KEY = "d22bbb2ebeec675fc174f42eae2669a180f1e58d0ea9d6ac2e14cc97a0343fbf"  # Get a free API key from https://serpapi.com/

bert_model = SentenceTransformer("all-MiniLM-L6-v2")

link = "https://www.huffpost.com/entry/diet-and-nutrition_b_5334195"
title,summary,keywords = article_scraper.extract_summary_and_keywords(link)

def search_similar_articles(query, num_results=10):
    """Search for similar articles using Google News via SerpAPI."""
    search_url = "https://serpapi.com/search"
    params = {   
        "engine": "google",
        "q": query,
        "api_key": SERP_API_KEY,
        "tbm": "nws",  # Google News
        "num": num_results,  # Number of results to retrieve
    }

    response = requests.get(search_url, params=params)
    if response.status_code != 200:
        return []

    data = response.json()
    results = []

    for article in data.get("news_results", []):
        results.append({
            "title": article.get("title"),
            "link": article.get("link"),
            "snippet": article.get("snippet")
        })

    return results




print(search_similar_articles(title))





# def check_opposing_articles(original_url):
#     """Find articles that challenge or dispute the original claim."""
#     title, summary, keywords = extract_summary_and_keywords(original_url)
#     print(f"\n🔎 Checking for opposing articles related to: {title}")

#     # Generate an "opposing search query"
#     query = f"opposite view of {title} OR fact-check {title} OR debunk {title}"
#     similar_articles = search_similar_articles(query)
#     if not similar_articles:
#         print("❌ No opposing articles found!")
#         return []

#     opposing_articles = []
    
#     # Compare similarity to check for opposing views
#     original_embedding = bert_model.encode(summary, convert_to_tensor=True)

#     for url in similar_articles:
#         try:
#             alt_title, alt_summary, _ = extract_summary_and_keywords(url)
#             alt_embedding = bert_model.encode(alt_summary, convert_to_tensor=True)
#             similarity = util.pytorch_cos_sim(original_embedding, alt_embedding).item()

#             # Consider articles with similarity < 0.5 as potential opposing views
#             if similarity < 0.5:
#                 opposing_articles.append((url, alt_title, similarity))
#         except:
#             continue  # Skip if extraction fails
    
#     if opposing_articles:
#         print("\n✅ Opposing Articles Found:")
#         for link, title, score in sorted(opposing_articles, key=lambda x: x[2]):
#             print(f"- {title} (Similarity: {score:.2f}) → {link}")
#     else:
#         print("❌ No strong opposing articles found!")

#     return opposing_articles

# Example Usage:
# original_url = "https://www.bbc.com/news/articles/c0mwln4p87do"  # Replace with a real news URL
# query = "Eating apple causes cancer" 
# print(search_similar_articles(query))

# print("-------------------------------")

# from googlesearch import search
# import requests
# from bs4 import BeautifulSoup
# from newspaper import Article
# import datetime
# import snscrape.modules.twitter as sntwitter
# import praw

# def get_article_date(url):
#     """Extracts publication date from a webpage"""
#     try:
#         article = Article(url)
#         article.download()
#         article.parse()
#         return article.publish_date  # Extract date if available
#     except:
#         return None  # Skip if extraction fails

# query = "Eating apple causes cancer"
# urls = [url for url in search(query, num_results=30)]

# articles = []

# for url in urls:
#     date = get_article_date(url)
#     if date:
#         articles.append((date, url))

# # Sort articles by earliest timestamp
# # articles.sort()

# print("\nEarliest Fake News Occurrence:")
# for date, url in articles:
#     print(f"📅 {date} - {url}")

# for url in urls:
#     page = requests.get(url)
#     soup = BeautifulSoup(page.text, 'html.parser')
#     print(soup.title.text + " - " + url)

# # # -----------------------------------
# # 📢 Reddit Search: Finding Early Misinformation Threads
# # -----------------------------------
# print("\n🔍 Searching Reddit for discussions...")

# reddit = praw.Reddit(client_id="unsKIQy6LF-Zj9vsd3hkdA", client_secret="SeDiX3g_3fT1GpbJmvzDugB45905gg", user_agent="find-fake-news-bot")
# submissions = reddit.subreddit("all").search(query, sort="new", limit=5)

# for submission in submissions:
#     print(f"\n📝 {submission.title} - {datetime.datetime.utcfromtimestamp(submission.created_utc)}")
#     print(f"🔗 {submission.url}")
