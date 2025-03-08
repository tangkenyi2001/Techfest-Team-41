from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from .rag_controller import query
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from fastapi import APIRouter
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from langchain_core.tools import StructuredTool
import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain.document_loaders.base import BaseLoader
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from langchain_core.tools import StructuredTool
from langchain.tools import Tool
load_dotenv()

router = APIRouter(prefix="/rag",tags=["rag"])

class userMessage(BaseModel):
    message: str

@router.post("/rag")
async def rag(request: userMessage)->str:
    try:
        model = init_chat_model("gpt-4", model_provider="openai")
        tools=[query]
        model_with_tools = model.bind_tools(tools)
        
        agent_executor = create_react_agent(model, tools)   
        response = await agent_executor.ainvoke({"messages": [HumanMessage(content=request.message)]})
        return response["messages"][-1].pretty_repr()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
