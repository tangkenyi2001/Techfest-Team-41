import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, BrowserConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer
import asyncio
from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
import requests
from xml.etree import ElementTree
import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader,BSHTMLLoader,UnstructuredMarkdownLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter,CharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langchain_core.tools import tool
from crawl4ai import AsyncWebCrawler
class State(TypedDict):
      question: str
      context: List[Document]
      answer: str

async def main():
    """Asynchronously crawl a webpage and return its content in markdown format, using crawl4ai.
    This function uses an asynchronous web crawler to fetch the content of the
    specified URL. The content is then converted to markdown format and returned.
    Args:
        url (str): The URL of the webpage to be crawled.
    Returns:
        Dict: A dictionary containing the source URL and the content of the webpage in markdown format.
    """
    query=" who is the minister of state"
    url=["https://www.straitstimes.com/singapore/politics/involuntarily-unemployed-can-get-monthly-payouts-by-going-for-activities-that-boost-job-chances","https://www.straitstimes.com/singapore/politics/more-spore-companies-offering-flexible-work-arrangements-in-2024-compared-to-before"]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = InMemoryVectorStore(embeddings)

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun_many(
            urls=url,
        )
    for i in range(len(result)):
        content=result[i].markdown
        all_splits = text_splitter.create_documents(content)
        _ = vector_store.add_documents(documents=all_splits)
        # docs = loader.load()
        # all_splits = text_splitter.split_documents(docs)
        # _ = vector_store.add_documents(documents=all_splits)
    # for i in url:
    #     loader = WebBaseLoader(
    #         web_paths=(i,),
    #         bs_kwargs=dict(
    #             parse_only=bs4.SoupStrainer(
    #                 class_=("post-content", "post-title", "post-header")
    #             )
    #         ),
    #     )
    #     docs = loader.load()
    #     all_splits = text_splitter.split_documents(docs)
    # Index chunks
       
    llm = init_chat_model("gpt-4o-mini", model_provider="openai")
    # Define prompt for question-answering
    prompt = hub.pull("rlm/rag-prompt")
    # Define application steps
    def retrieve(state: State):
        retrieved_docs = vector_store.similarity_search(state["question"],k=3)
        return {"context": retrieved_docs}


    def generate(state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = prompt.invoke({"question": state["question"], "context": docs_content})
        response = llm.invoke(messages)
        return {"answer": response.content}


    # Compile application and test
    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()
    response = graph.invoke({"question":query})
    return response['answer']

if __name__ == "__main__":
    asyncio.run(main())