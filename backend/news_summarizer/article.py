from .article_scraper import NewsRequest
from fastapi import APIRouter

router = APIRouter(
    prefix="/newssummary",
    tags=["newssummary"],
    responses={404: {"description": "Not found"}},
)

@router.post("/get_news_info")  
async def get_news_info(request: NewsRequest):
    try:
        summary, keyword = request.extract_summary_and_keywords(request.url)
        relevant_articles = request.search_similar_articles(summary)
        return {
            "summary": summary,
            "keywords": keyword  ,
            "relevant_articles": relevant_articles,
        }
    except Exception as e:
        return {"error": str(e)}
