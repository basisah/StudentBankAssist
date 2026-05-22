from fastapi import FastAPI, HTTPException
from models import ChatRequest, ChatResponse, EscalateRequest, EscalateResponse
from chat.engine import chat
from chat.escalation import should_escalate
from chat.engine import context_history
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse


app = FastAPI(title="RBC Account Assistant", version="1.0.0")
@app.get("/")
async def serve_chat():
    return FileResponse("chat.html")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    result = chat(req.message,req.session_id,)
    escalate = should_escalate(req.message, result["response"])
    return ChatResponse(
        session_id=req.session_id,
        response=result["response"],
        sources=result["sources"],
        escalate=escalate
    )

@app.get("/chat/{session_id}/history")
async def get_history(session_id: str):
    if session_id not in context_history:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "history": context_history[session_id]}

@app.post("/escalate", response_model=EscalateResponse)
async def escalate(req: EscalateRequest):
    return EscalateResponse(message="Connecting you to RBC support...")

@app.get("/products")
async def list_products():
    # Returns top-level account categories from knowledge base
    return {"categories": ["Chequing", "Savings", "TFSA", "RRSP", "FHSA", "Credit Cards", "Mortgages"]}

@app.get("/health")
async def health():
    return {"status": "ok", "model": "gpt-4o-mini"}

@app.get("/docs-url")
async def docs():
    return {"swagger": "/docs", "redoc": "/redoc"}