from fastapi import FastAPI
from agent_rag import agent
app = FastAPI()

app.include_router(agent.router)
@app.get("/")
async def root():
    return {"message": "Hello World"}