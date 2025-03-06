from newspaper import Article
from keybert import KeyBERT
import nltk

nltk.download("punkt")  # Ensure NLTK tokenizer is available

def extract_summary_and_keywords(url, num_keywords=5):
    article = Article(url)
    article.download()
    article.parse()
    article.nlp()

    # Extractive summary from newspaper3k
    summary = article.summary

    # Keyword extraction using KeyBERT
    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(article.text, keyphrase_ngram_range=(1, 2), stop_words='english', top_n=num_keywords)
    
    return summary, [kw[0] for kw in keywords]  # Return summary and keywords

if __name__ == "__main__":
    url = "https://www.bbc.com/news/world-12345678"  # Replace with actual news article URL
    summary, keywords = extract_summary_and_keywords(url)
    
    print("Extracted Summary:\n", summary)
    print("\nExtracted Keywords:", keywords)
