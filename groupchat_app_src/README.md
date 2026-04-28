# Group Chat Web App + Offline Llama 3 Bot

FastAPI + MySQL + vanilla HTML/JS group chat with an offline Llama 3 bot. The backend can call a local OpenAI-compatible Llama server, or directly load a local GGUF model with `llama-cpp-python`.

## Quick Start (Dev)

```bash
# 1) MySQL
# create DB & user, or run sql/schema.sql

# 2) Backend
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# copy env and edit values
cp ../.env.example ../.env

# 3) Start a local Llama 3 server
# Example with llama.cpp:
# ./llama-server -m /path/to/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf \
#   --host 0.0.0.0 --port 8001 --ctx-size 4096

# 4) Run app
uvicorn app:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000

The default `.env` uses `LLM_PROVIDER=llama_cpp_server` and `LLM_API_BASE=http://localhost:8001/v1`, so no OpenAI cloud API is used.

## Direct GGUF Mode

If you do not want to run a separate model server:

```bash
pip install llama-cpp-python
```

Then update `../.env`:

```env
LLM_PROVIDER=llama_cpp
LLAMA_MODEL_PATH=/path/to/Meta-Llama-3-8B-Instruct.Q4_K_M.gguf
LLAMA_N_CTX=4096
LLAMA_N_GPU_LAYERS=-1
```
