# RBC Account Assistant

An AI-powered chatbot that answers questions about RBC banking products using real scraped data from RBC's public product pages and Government of Canada financial guidance. Built with a RAG (Retrieval Augmented Generation) architecture to ensure every response is grounded in actual source data — not hallucinated.

## Tech Stack

- **Backend:** FastAPI, Pydantic v2, Uvicorn
- **AI/ML:** OpenAI GPT-4o-mini, text-embedding-3-small, LangChain-style RAG pipeline
- **Vector Database:** ChromaDB (local persistent storage)
- **Web Scraping:** BeautifulSoup4, Requests
- **Testing:** pytest, pytest-asyncio, httpx
- **Infrastructure:** Docker, Docker Compose, GitHub Actions CI/CD

## Architecture

```
User Message
     │
     ▼
┌──────────┐     ┌──────────────┐     ┌───────────┐
│ FastAPI   │────▶│ Embed Query  │────▶│ ChromaDB  │
│ /chat     │     │ (OpenAI)     │     │ Vector DB │
└──────────┘     └──────────────┘     └─────┬─────┘
                                            │
                                    Top 4 chunks
                                            │
                                            ▼
                                   ┌────────────────┐
                                   │ GPT-4o-mini     │
                                   │ + Context       │
                                   │ + Chat History  │
                                   └───────┬────────┘
                                           │
                                           ▼
                                   Grounded Response
                                   + Source Citations
                                   + Escalation Check
```

## How RAG Works

1. **Scraping** — BeautifulSoup scrapes RBC product pages and Canada.ca financial guidance pages, storing clean text in `data/scraped/`.
2. **Chunking** — Scraped text is split into overlapping 400-word chunks (50-word overlap) so context isn't lost at boundaries.
3. **Embedding** — Each chunk is converted to a 1536-dimensional vector using OpenAI's `text-embedding-3-small` model.
4. **Storing** — Vectors and their source text are stored in ChromaDB for fast semantic search.
5. **Retrieval** — When a user asks a question, the query is embedded and the top 4 most similar chunks are retrieved.
6. **Generation** — Retrieved chunks are fed as context to GPT-4o-mini, which generates a response grounded in real RBC data.

## Data Sources

| Source | URL | Content |
|--------|-----|---------|
| RBC Chequing Accounts | rbcroyalbank.com/bank-accounts/chequing-accounts/ | Day-to-day, Advantage, No Limit, VIP banking |
| RBC Savings Accounts | rbcroyalbank.com/bank-accounts/savings-accounts/ | Enhanced, High Interest, Day-to-day savings |
| RBC TFSA | rbcdirectinvesting.com/accounts-investments/tfsa.html | RBC's TFSA product details |
| Canada.ca — TFSA | canada.ca/.../tax-free-savings-account.html | Official TFSA rules, contribution limits |
| NOMI Find & Save | rbcroyalbank.com/bank-accounts/nomi-find-and-save.html | Automated savings feature |

## Project Structure

```
rbcAssist/
├── main.py                  # FastAPI app entry point
├── models.py                # Pydantic request/response models
├── rag/
│   ├── scraper.py           # BeautifulSoup scraper for RBC + Canada.ca
│   ├── ingest.py            # Chunk, embed, store in ChromaDB
│   └── retriever.py         # Query ChromaDB by semantic similarity
├── chat/
│   ├── engine.py            # RAG pipeline + GPT-4o-mini integration
│   └── escalation.py        # Escalation trigger detection
├── tests/
│   ├── test_scraper.py      # Scraper unit tests
│   ├── test_ingest.py       # Ingest pipeline tests (mocked OpenAI)
│   └── test_escalation.py   # Escalation logic tests
├── data/
│   └── scraped/             # Auto-generated scraped content (gitignored)
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI pipeline
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env                     # OpenAI API key (gitignored)
```

## Setup

### Prerequisites

- Python 3.11+
- OpenAI API key

### Local Development

```bash
# Clone the repo
git clone https://github.com/basisah/rbcAssist.git
cd rbcAssist

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set your OpenAI API key
echo 'OPENAI_API_KEY=sk-your-key-here' > .env

# Scrape data sources
python -c "from rag.scraper import scrape_all; scrape_all()"

# Ingest into ChromaDB
python -c "from rag.ingest import ingest_all; ingest_all()"

# Start the server
uvicorn main:app --reload
```

The API is now live at `http://localhost:8000`. Visit `http://localhost:8000/docs` for the interactive Swagger UI.

### Docker

```bash
docker compose up --build

# Then scrape and ingest
docker compose run app python -c "from rag.scraper import scrape_all; scrape_all()"
docker compose run app python -c "from rag.ingest import ingest_all; ingest_all()"
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Send a message and get a grounded response |
| `GET` | `/chat/{session_id}/history` | Retrieve conversation history for a session |
| `POST` | `/escalate` | Request human agent contact info |
| `GET` | `/products` | List available account categories |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI (auto-generated by FastAPI) |

### Example Request

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "user-001", "message": "What is an RBC TFSA?"}'
```

### Example Response

```json
{
  "session_id": "user-001",
  "response": "An RBC TFSA (Tax-Free Savings Account) allows you to save and invest without paying tax on the growth...",
  "sources": [
    {
      "document": "A TFSA is a registered savings account that lets you earn...",
      "source_file": "rbc_TFSA.txt"
    }
  ],
  "escalate": false,
  "timestamp": "2026-05-20T12:00:00"
}
```

## Escalation

The chatbot automatically detects when a user needs human support. Triggers include keywords like fraud, lost card, complaint, and locked out, as well as low-confidence bot responses. When escalation is triggered, the response includes RBC's real contact options:

- **Phone:** 1-800-769-2511
- **Web:** https://www.rbc.com/contact-us.html
- **Online Banking:** https://www.rbc.com/online-banking.html

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test files
pytest tests/test_scraper.py -v
pytest tests/test_ingest.py -v
pytest tests/test_escalation.py -v
```

Tests cover scraper functionality, chunking logic, embedding pipeline (mocked), escalation trigger detection, and input validation. CI runs the full test suite on every push via GitHub Actions.

## CI/CD

Every push to `main` triggers the GitHub Actions CI pipeline which installs dependencies, runs the full pytest suite, and reports pass/fail status on the commit. The workflow is defined in `.github/workflows/ci.yml`.

---

Built by **Basisah Musarrat** — Computer Science, University of Saskatchewan