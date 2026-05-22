# tests/test_api.py
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, MagicMock
from main import app


transport = ASGITransport(app=app)


# ========== Health endpoint ==========

@pytest.mark.asyncio
async def test_health_returns_ok():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
        assert r.json()["model"] == "gpt-4o-mini"


# ========== Products endpoint ==========

@pytest.mark.asyncio
async def test_products_returns_categories():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/products")
        assert r.status_code == 200
        assert "categories" in r.json()
        assert "Chequing" in r.json()["categories"]
        assert "TFSA" in r.json()["categories"]


# ========== Docs URL endpoint ==========

@pytest.mark.asyncio
async def test_docs_url_returns_paths():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/docs-url")
        assert r.status_code == 200
        assert r.json()["swagger"] == "/docs"
        assert r.json()["redoc"] == "/redoc"


# ========== Chat endpoint ==========

@pytest.mark.asyncio
@patch("main.chat")
@patch("main.should_escalate")
async def test_chat_valid_request(mock_escalate, mock_chat):
    mock_chat.return_value = {
    "response": "A TFSA is a tax-free savings account.",
    "sources": [{"document": "TFSA info", "metadata": {"source": "rbc_tfsa.txt"}}]  # this line
}
    mock_escalate.return_value = False

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/chat", json={
            "session_id": "test-001", "message": "What is an RBC TFSA?"
        })
        assert r.status_code == 200
        assert "response" in r.json()
        assert "sources" in r.json()
        assert r.json()["escalate"] is False


@pytest.mark.asyncio
async def test_chat_empty_message_rejected():
    """Pydantic should reject empty messages with 422"""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/chat", json={"session_id": "s1", "message": ""})
        assert r.status_code == 422


@pytest.mark.asyncio
async def test_chat_missing_session_id():
    """Pydantic should reject requests without session_id"""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/chat", json={"message": "hello"})
        assert r.status_code == 422


@pytest.mark.asyncio
async def test_chat_missing_message():
    """Pydantic should reject requests without message"""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/chat", json={"session_id": "s1"})
        assert r.status_code == 422


@pytest.mark.asyncio
@patch("main.chat")
@patch("main.should_escalate")
async def test_chat_escalation_triggers_on_fraud(mock_escalate, mock_chat):
    mock_chat.return_value = {
    "response": "I detect suspicious activity.",
    "sources": [{"document": "fraud info", "metadata": {"source": "rbc.txt"}}]  # this line
}
    mock_escalate.return_value = True

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/chat", json={
            "session_id": "s2", "message": "I think there is fraud on my account"
        })
        assert r.json()["escalate"] is True


# ========== Escalate endpoint ==========

@pytest.mark.asyncio
async def test_escalate_returns_contact_info():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/escalate", json={"session_id": "s1"})
        assert r.status_code == 200
        assert "1-800-769-2511" in r.json()["phone"]
        assert r.json()["message"] == "Connecting you to RBC support..."


@pytest.mark.asyncio
async def test_escalate_with_reason():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/escalate", json={
            "session_id": "s1", "reason": "Unauthorized transaction"
        })
        assert r.status_code == 200


# ========== History endpoint ==========

@pytest.mark.asyncio
async def test_history_returns_404_for_unknown_session():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/chat/nonexistent-session/history")
        assert r.status_code == 404