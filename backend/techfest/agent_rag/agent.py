import getpass
import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from agent_rag.tools.rag import query
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
import asyncio
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from fastapi import APIRouter
from fastapi import Request
from fastapi import APIRouter, Depends, HTTPException
import requests
from pydantic import BaseModel
import json
load_dotenv()
router = APIRouter()
if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

class userMessage(BaseModel):
    message: str
@router.post("/test")
async def print(request: userMessage):
    return {"hello": request.message}

@router.post("/rag")
async def rag(request: userMessage):
    try:
        llm = init_chat_model("gpt-4", model_provider="openai")
        tools=[query]
        agent_executor = create_react_agent(llm, tools)
        response = agent_executor.invoke({"messages": [HumanMessage(content=request.message)]})
        return response["messages"][-1].pretty_repr()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# print(rag("what is Generative Agents Simulation? one url u can use is https://lilianweng.github.io/posts/2023-06-23-agent/"))