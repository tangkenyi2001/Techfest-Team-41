from article_scraper import extract_summary_and_keywords

# import nltk
# nltk.download('punkt_tab')

if __name__ == "__main__":
    # Input: News article URL
    news_url = "https://www.bbc.com/news/articles/c3w14gw3wwlo" 

    summary, keywords = extract_summary_and_keywords(news_url)
    print("Extracted Keywords:", summary)