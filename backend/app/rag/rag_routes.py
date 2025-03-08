from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from .rag_controller import query
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from fastapi import APIRouter
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel,Field
from fastapi.responses import JSONResponse
load_dotenv()
router = APIRouter()

class userMessage(BaseModel):
    message: str

class ResponseFormatter(BaseModel):
    """Always use this tool to structure your response to the user."""
    verdict: str = Field(description="The answer to the user's question,{Topic} is REAL/FAKE")
    explanation: str = Field(description="How it came to this decision with the context fetched")
    sources: list[str] 

@router.post("/rag")
async def rag(request: userMessage)->str:
    try:
        llm = init_chat_model("gpt-4o-mini", model_provider="openai")
        tools=[query]
        agent_executor = create_react_agent(llm, tools,response_format=ResponseFormatter)
        response = agent_executor.invoke({"messages": [HumanMessage(content=request.message)]})
        # print(response)
        response_dict = response["structured_response"]
        if isinstance(response_dict, ResponseFormatter):
            response_dict = response_dict.dict()
        
        # Return a proper JSONResponse
        return JSONResponse(content=response_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
