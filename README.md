# RAGChatbot

Offline Llama 3 chatbot project with two working parts:

- `embedding/`: Streamlit RAG app for uploading documents, embedding them locally, and asking grounded questions.
- `groupchat_app_src/`: FastAPI + MySQL group chat app with an offline Llama 3 bot.

No OpenAI cloud API is required for the current setup. The chat model runs locally through `llama.cpp`, and the RAG app uses local sentence-transformers embeddings with FAISS.

## Project Structure

```text
RAGChatbot/
├── embedding/                 # Local RAG Streamlit app
│   ├── app.py
│   ├── htmlTemplates.py
│   ├── readme.md
│   └── requirements.txt
├── groupchat_app_src/         # Group chat web app
│   ├── backend/               # FastAPI backend
│   ├── frontend/              # HTML/CSS/JS frontend
│   ├── sql/                   # MySQL schema
│   ├── twa_android_src/       # Android TWA wrapper
│   ├── .env.example
│   └── README.md
├── models/                    # Local GGUF models, ignored by git
├── .gitignore
└── README.md
```

## Local Model

This repo expects a local Llama 3 GGUF model, for example:

```text
models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf
```

Start the local Llama 3 server:

```bash
/Users/fuyaozhao/llama.cpp/build/bin/llama-server \
  -m /Users/fuyaozhao/Desktop/RAGChatbot/models/Meta-Llama-3-8B-Instruct-Q4_K_M.gguf \
  --host 0.0.0.0 \
  --port 8001 \
  --ctx-size 4096
```

Test it:

```bash
curl -s http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"llama-3-8b-instruct","messages":[{"role":"user","content":"Say offline llama ok"}],"max_tokens":16}'
```

## Run the RAG App

Install dependencies:

```bash
cd embedding
pip install -r requirements.txt
```

Run Streamlit:

```bash
streamlit run app.py --server.port 8502
```

Open:

```text
http://localhost:8502
```

Workflow:

1. Upload one or more PDF, TXT, MD, or HTML files.
2. Click `Process documents`.
3. Ask questions in the chat box.
4. The app retrieves the closest chunks from FAISS and asks local Llama 3 to answer using only that context.

Default RAG settings:

```env
RAG_LLM_API_BASE=http://localhost:8001/v1
RAG_LLM_MODEL=llama-3-8b-instruct
RAG_LLM_API_KEY=local-llama
RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## Run the Group Chat App

Create the MySQL database and user:

```sql
CREATE DATABASE groupchat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'chatuser'@'localhost' IDENTIFIED BY 'chatpass';
GRANT ALL PRIVILEGES ON groupchat.* TO 'chatuser'@'localhost';
FLUSH PRIVILEGES;
```

Install backend dependencies:

```bash
cd groupchat_app_src/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create config:

```bash
cp ../.env.example ../.env
```

Important `.env` values:

```env
DATABASE_URL=mysql+asyncmy://chatuser:chatpass@localhost:3306/groupchat
LLM_PROVIDER=llama_cpp_server
LLM_API_BASE=http://localhost:8001/v1
LLM_MODEL=llama-3-8b-instruct
APP_PORT=8002
```

Run the backend:

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8002
```

Open:

```text
http://localhost:8002
```

Messages containing `?` trigger the Llama 3 bot.

## Notes

- `models/`, `.env`, virtual environments, logs, cache files, and generated build outputs are ignored by git.
- Do not commit Hugging Face tokens, API keys, database passwords, or local model files.
- If `localhost:8000` is already occupied, use `8002` as shown above.
- The first local Llama 3 response can be slower because the model needs to load and warm up.
