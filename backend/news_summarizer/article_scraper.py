from newspaper import Article
from keybert import KeyBERT
from pydantic import BaseModel
from transformers import pipeline
import requests


# Load the summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
link = "https://www.huffpost.com/entry/diet-and-nutrition_b_5334195"
SERP_API_KEY = "d22bbb2ebeec675fc174f42eae2669a180f1e58d0ea9d6ac2e14cc97a0343fbf"

class NewsRequest(BaseModel):
    url: str  # Input: News article URL

    def extract_summary_and_keywords(url, num_keywords=5):
        article = Article(url)
        article.download()
        article.parse()

        title = article.title  # Extract title
        text = article.text.strip()

        # Generate summary using BART
        if len(text.split()) > 50:  
            summary = summarizer(text, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]
        else:
            summary = text  

        # Extract keywords using KeyBERT
        kw_model = KeyBERT()
        keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=num_keywords)

        return title, summary, [kw[0] for kw in keywords]  # Return title, summary, and keywords

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


