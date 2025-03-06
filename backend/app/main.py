from fastapi import FastAPI
from .whatsapp import whatsapp

app = FastAPI()

app.include_router(whatsapp.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}