From python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python -c "from rag.scraper import scrape_all; scrape_all()"
RUN python -c "from rag.ingest import ingest_all; ingest_all()"
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0", "--port", "8000"]
