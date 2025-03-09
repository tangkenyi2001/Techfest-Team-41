
We introduce CheckFirstLeh as a Telegram Bot and Website that uses an Agentic Retrieval-Augmented Generation (RAG) approach to enhance fact-checking. It combines the strengths of information retrieval with the LLMs' ability to generate, allowing for more precise and relevant judgments.
As misinformation becomes more varied and harder to recognize, and AI generative produces more convincing content, it's essential to stay. If even technology-savvy teenagers cannot distinguish real from unreal news, it is much harder for the elderly
How it works:
1. Real-Time Information Retrieval: When a user submits a question, the system retrieves relevant documents from trusted sources.
2.  Scraping and Vectorization: The agent scrapes the content of the pages and saves them in a vector database. The information is transformed into vector representations for semantic comparison efficiently.
3.  Contextual Retrieval: The documents most semantically similar to the query are retrieved from the vector database.
4.  Decision-Making & Generation with Enhanced Context: The system combines outside, factual sources with its own understanding of the query and generates a more accurate response based on the enhanced context.
5.  Transparency and Interpretability: The user can see what sources were consulted, in what order they were ranked, and how the model made its decision.
