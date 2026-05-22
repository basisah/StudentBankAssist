import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="bank")


#Break down the scraped data into smaller chunks
def chunk(text: str, size= 400, overlap= 50) -> list[str]:
    words = text.split()
    chunks = []
    i= 0
    while i < len(words):
        chunk = " ".join(words[i:i+size])
        chunks.append(chunk)
        i += size - overlap
    return chunks

#Create vector embeddings for the chunks of data
def embed(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(input=texts, model="text-embedding-3-small")
    return [embedding.embedding for embedding in response.data]

#Store the vector embeddings in a vector database
def ingest_all():
    for fname in os.listdir("data/scraped"):
        with open(f"data/scraped/{fname}", "r") as f:
            text = f.read()
        chunks = chunk(text)
        embeddings = embed(chunks)
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=[f"{fname}_{i}" for i in range(len(chunks))],
            metadatas=[{"source": fname} for _ in range(len(chunks))]
        )
        print(f"Ingested {len(chunks)} chunks from {fname}")

