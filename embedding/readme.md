# Custom Content Chatbot Using Local Llama 3, Local Embeddings, and FAISS

This Streamlit application follows Lab Assignment 8 Part 3. It lets users upload PDFs and text files, extracts document text, splits the text into chunks, embeds the chunks with a local sentence-transformers model, stores them in a FAISS vector database, and answers questions with a local offline Llama 3 model.


## How it works

1. The web application is built with Streamlit.
2. Users upload one or more PDF, TXT, MD, or HTML documents in the sidebar.
3. The app extracts document text and splits it into 500-character chunks with overlap.
4. A local embedding model converts the chunks into vectors.
5. FAISS stores the vectors and retrieves the chunks closest to the user's question.
6. LangChain builds a conversational retrieval chain.
7. The local Llama 3 chat model answers using only the retrieved document context.


## Requirements
1. Install the required Python packages:
```
pip install -r requirements.txt
```

2. Start the local Llama 3 server before running the Streamlit app:
```
/Users/fuyaozhao/llama.cpp/build/bin/llama-server \
  -m /Users/fuyaozhao/Desktop/RAGChatbot/models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf \
  --host 0.0.0.0 \
  --port 8001 \
  --ctx-size 4096
```

Optional `.env` values:
```
RAG_LLM_API_BASE=http://localhost:8001/v1
RAG_LLM_MODEL=llama-3-8b-instruct
RAG_LLM_API_KEY=local-llama
RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```


## Code Structure

The code is structured as follows:

- `app.py`: The main application file that defines the Streamlit GUI and RAG pipeline.
    * `get_document_text`: reads text from uploaded PDFs and text files.
    * `get_text_chunks`: splits extracted text into chunks of size 500.
    * `get_vectorstore`: creates a FAISS vector store from text chunks and local embeddings.
    * `get_conversation_chain`: creates the conversational retrieval chain using local Llama 3.
    * `handle_userinput`: sends user questions to the chain and stores chat history.
- `htmlTemplates.py`: A module that defines HTML templates for the user interface.
- `requirements.txt`: Python dependencies for this part of the lab.


## How to run
```
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal, upload documents from the sidebar, click **Process documents**, and ask questions in the chat box.
