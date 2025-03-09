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
        all_splits = text_splitter.split_text(docs)
    # Index chunks
        _ = vector_store.add_documents(documents=all_splits)
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

