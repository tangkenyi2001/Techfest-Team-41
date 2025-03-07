from fastapi import FastAPI
from news_summarizer.article import router as article_router



app = FastAPI()

app.include_router(article_router)
@app.get("/")
async def root():
    return {"message": "Hello World"}
