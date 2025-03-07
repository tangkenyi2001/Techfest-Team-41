from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from .rag_controller import query
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from fastapi import APIRouter
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

load_dotenv()
router = APIRouter()

class userMessage(BaseModel):
    message: str


@router.post("/rag")
async def rag(request: userMessage)->str:
    try:
        llm = init_chat_model("gpt-4", model_provider="openai")
        tools=[query]
        agent_executor = create_react_agent(llm, tools)
        response = agent_executor.invoke({"messages": [HumanMessage(content=request.message)]})
        return response["messages"][-1].pretty_repr()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
