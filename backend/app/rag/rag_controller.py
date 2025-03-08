import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate

load_dotenv()
# Load and chunk contents of the blog
class State(TypedDict):
      question: str
      context: List[Document]
      answer: str

@tool
def query(query: str,url: List[str])-> str:
    """ Chunk a website with the given url and measure similarity with user query, allowing it
    to find similar information to answer user query.

    Args:
        query: query of User
        url: List of urls provided by User
    """
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=200)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = InMemoryVectorStore(embeddings)
    for i in url:
        loader = WebBaseLoader(
            web_paths=(i,),
            bs_kwargs=dict(
                parse_only=bs4.SoupStrainer(
                    class_=("post-content", "post-title", "post-header")
                )
            ),
        )
        docs = loader.load()
        all_splits = text_splitter.split_documents(docs)
    # Index chunks
        _ = vector_store.add_documents(documents=all_splits)
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
    def retrieve(state: State):
        retrieved_docs = vector_store.similarity_search(state["question"],k=3)
        return {"context": retrieved_docs}

    def generate(state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = prompt.invoke({"question": state["question"], "context": docs_content})
        response = llm.invoke(messages)
        return {"answer": response}

    

    # Compile application and test
    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()
    response = graph.invoke({"question":query})
    return response['answer']

