# RBC Account Assistant

AI-powered chatbot that answers questions about RBC banking products using scraped data from RBC and Government of Canada websites. Built with RAG (Retrieval Augmented Generation) so every response is grounded in real data, not hallucinated.


##What it looks like
<img width="2864" height="1548" alt="image" src="https://github.com/user-attachments/assets/b2ef3e96-4a8f-487d-99ac-6133e7b3e8d5" />


## Tech Stack

FastAPI · Pydantic v2 · OpenAI GPT-4o-mini · ChromaDB · BeautifulSoup4 · pytest · Docker

## How It Works

1. **Scrape** — BeautifulSoup pulls RBC product pages and Canada.ca financial guidance
2. **Chunk** — Text is split into overlapping 400-word chunks
3. **Embed** — Chunks are converted to vectors using OpenAI text-embedding-3-small
4. **Store** — Vectors saved in ChromaDB for semantic search
5. **Retrieve** — User query is embedded, top 4 matching chunks are found
6. **Generate** — GPT-4o-mini answers using only the retrieved context

## Setup

```bash
git clone https://github.com/basisah/rbcAssist.git
cd rbcAssist
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo 'OPENAI_API_KEY=your-key-here' > .env
```

## Run

```bash
# 1. Scrape data
python -c "from rag.scraper import scrape_all; scrape_all()"

# 2. Ingest into ChromaDB
python -c "from rag.ingest import ingest_all; ingest_all()"

# 3. Start server
uvicorn main:app --reload
```

Chat UI: `http://localhost:8000`
Swagger docs: `http://localhost:8000/docs`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Chat interface |
| `POST` | `/chat` | Send a message |
| `GET` | `/chat/{session_id}/history` | Get conversation history |
| `POST` | `/escalate` | Get RBC contact info |
| `GET` | `/products` | List account categories |
| `GET` | `/health` | Health check |

## Testing

```bash
pytest tests/ -v
```

CI runs automatically on every push via GitHub Actions.

## Docker

```bash
docker compose up --build
```

---
Basisah Musarrat
