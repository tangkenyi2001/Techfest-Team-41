from fastapi import FastAPI
#from .whatsapp import whatsapp
from api_routers.webscrape import router as webscrape_router

app = FastAPI()

#app.include_router(whatsapp.router)
app.include_router(webscrape_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}