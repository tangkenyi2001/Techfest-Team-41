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
from langchain.prompts import PromptTemplate
load_dotenv()
# Load and chunk contents of the blog
class State(TypedDict):
      question: str
      context: List[Document]
      answer: str

async def querytool(query: str,url: List[str])-> str:
    """ Chunk a website with the given url and measure similarity with user query, allowing it
    to find similar information to answer user query.

    Args:
        query: query of User
        url: List of urls provided by User
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = InMemoryVectorStore(embeddings)
    browser_config = BrowserConfig()  # Default browser configuration
    llm = init_chat_model("gpt-4o-mini", model_provider="openai")
    # Define prompt for question-answering
    prompt = PromptTemplate.from_template("""
    You are a helpful anti-fake news AI assistant that answers questions based on the provided context and differentiates real news and fake news.The provided context are real news found on the internet. Your job is
    to verify if the question is a real or fake news using the context.                              

    Context:
    {context}

    Statement: {question}

    Instructions:
    - Answer the question based ONLY on the context provided
    - If the context doesn't contain the answer, say "I don't have enough information to answer this question"
    - Keep your answer concise and to the point
    - If appropriate, cite the relevant parts of the context and include it in your answer
    - Give explanations for your answers
    - Always include the source, including the url.
    - Always answer either "FAKE" or "REAL" at the start   
    - Show the comparison between the context and the statement to show what exactly is wrong, and what should be correct.                                                                                                                                                   
                                        

    Answer:
    """)
    # Define application steps
    prune_filter = PruningContentFilter(
        # Lower → more content retained, higher → more content pruned
        threshold=0.45,           
        # "fixed" or "dynamic"
        threshold_type="dynamic",  
        # Ignore nodes with <5 words
        min_word_threshold=20      
    )

    # Step 2: Insert it into a Markdown Generator
    md_generator = DefaultMarkdownGenerator(content_filter=prune_filter)

    # Step 3: Pass it to CrawlerRunConfig
    config = CrawlerRunConfig(
        markdown_generator=md_generator
    )
    async with AsyncWebCrawler(config=browser_config) as crawler:
        try:
            result = await crawler.arun_many(
                urls=url,
                config=config
            )
            
            if not result:
                error_message = "No results retrieved from web crawler."
                print(error_message)
                raise ValueError(error_message)  # Raise a specific exception
                        
            print(f"Successfully retrieved {len(result)} pages")
            
            # Process results only if we have them
            for i in range(len(result)):
                metadata = {"url": result[i].url}
                content = result[i].markdown
                # print(result[i].markdown)
                docs=[Document(page_content=content, metadata=metadata)]
                all_splits = text_splitter.split_documents(docs)
                _ = vector_store.add_documents(documents=all_splits)
        except Exception as e:
            print(f"Error during crawling: {e}")

    
    def retrieve(state: State):
        
        retrieved_docs = vector_store.similarity_search(state["question"],k=3)
        return {"context": retrieved_docs}


    def generate(state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = prompt.invoke({"question": state["question"], "context": docs_content})
        response = llm.invoke(messages)
        return {"answer": response.content}


    # Compile application and test
    graph_builder = StateGraph(State).add_sequence([retrieve,generate])
    graph_builder.add_edge(START, "retrieve")
    graph_builder.add_edge("generate", END)
    graph = graph_builder.compile()
    response = graph.invoke({"question":query})
    print(response['answer'])
    return response['answer']
query = StructuredTool.from_function(coroutine=querytool)
if __name__ == "__main__":
    asyncio.run(querytool("Under the Singapore Green Plan 2030, the goal is to reduce household water to 130 litres per day",["https://www.straitstimes.com/singapore/each-persons-daily-water-use-crept-up-to-142-litres-in-2024-one-litre-higher-than-past-year","https://www.straitstimes.com/singapore/fewer-o-level-subjects-for-jc-admission-could-ease-academic-pressure-students-and-parents"]))