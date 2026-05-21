# The full rag pipeline is here
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
chroma = chromadb.PersistentClient(path="./chroma_db")
collection = chroma.get_or_create_collection(name="bank")

#System prompt for the bot to use when generating responses

system_prompt = """ You are a RBC personal banking assistant. Answer the questions about RBC products and services using only the context provided. If you cannot answer from the context,
 say you don't know. If the user asks for information that is not in the context, say you cannot provide that information. If the user asks for help or seems confused, recommend they contact RBC directly. Always be polite and professional. 
 Always be accurate - never guuess or make up informatiion, especially about fees, interest rates, or account details.
"""

#in memory context history to provide context for the bot
context_history : dict[str, list] = {}

def retrieve(query: str, top_k: int=4) -> list[dict]:
    """
    Retrieve relevant context from the vector database based on the user's query.

    Args:
        query (str): The user's input query.

    Returns:
        list[dict]: A list of relevant context dictionaries.
    """
    query_vector = client.embeddings.create(input = [query], model="text-embedding-3-small").data[0].embedding
    results = collection.query(
        query_embeddings = [query_vector],
        n_results = top_k)
    return [{"document": d, "metadata": m} for d, m in zip(results['documents'][0], results['metadatas'][0])]



def chat(user_input: str, session_id: str) -> dict:
    """
    Generate a response to the user's input using retrieved context and the system prompt.

    Args:
        user_input (str): The user's input message.
        session_id (str): The session identifier.

    Returns:
        dict: A dictionary containing the response and sources."""
    
    sources = retrieve(user_input)
    context = "\n\n".join([s["document"] for s in sources])

    history = context_history.get(session_id, [])
    history.append({"role": "user", "content": user_input})
    
    messages = [
        {"role": "system", "content": f"{system_prompt}\n\nContext:\n{context}"},
        *history[-6:]  # keep last 3 exchanges for context window efficiency
    ]
    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=messages, max_tokens=500
    )
    reply = response.choices[0].message.content
    history.append({"role": "assistant", "content": reply})
    context_history[session_id] = history
    return {"response": reply, "sources": sources}
    



