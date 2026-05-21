# tests/test_engine.py
import pytest
from unittest.mock import patch, MagicMock


# ========== retrieve() tests ==========

@patch("chat.engine.collection")
@patch("chat.engine.client")
def test_retrieve_returns_list_of_dicts(mock_client, mock_collection):
    """retrieve() should return a list of dicts with document and metadata"""
    from chat.engine import retrieve

    # Mock embedding response
    mock_embedding = MagicMock()
    mock_embedding.embedding = [0.1, 0.2, 0.3]
    mock_client.embeddings.create.return_value = MagicMock(data=[mock_embedding])

    # Mock ChromaDB response
    mock_collection.query.return_value = {
        "documents": [["RBC offers a TFSA", "TFSA contribution limit is $7000"]],
        "metadatas": [[{"source": "rbc_tfsa.txt"}, {"source": "canada_tfsa.txt"}]]
    }

    results = retrieve("What is a TFSA?")
    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["document"] == "RBC offers a TFSA"
    assert results[0]["metadata"]["source"] == "rbc_tfsa.txt"


@patch("chat.engine.collection")
@patch("chat.engine.client")
def test_retrieve_uses_correct_embedding_model(mock_client, mock_collection):
    """retrieve() should use text-embedding-3-small"""
    from chat.engine import retrieve

    mock_embedding = MagicMock()
    mock_embedding.embedding = [0.1]
    mock_client.embeddings.create.return_value = MagicMock(data=[mock_embedding])
    mock_collection.query.return_value = {"documents": [[]], "metadatas": [[]]}

    retrieve("test query")
    mock_client.embeddings.create.assert_called_once_with(
        input=["test query"], model="text-embedding-3-small"
    )


@patch("chat.engine.collection")
@patch("chat.engine.client")
def test_retrieve_queries_chromadb_with_embedding(mock_client, mock_collection):
    """retrieve() should pass the embedding vector to ChromaDB"""
    from chat.engine import retrieve

    mock_embedding = MagicMock()
    mock_embedding.embedding = [0.1, 0.2, 0.3]
    mock_client.embeddings.create.return_value = MagicMock(data=[mock_embedding])
    mock_collection.query.return_value = {"documents": [[]], "metadatas": [[]]}

    retrieve("test")
    mock_collection.query.assert_called_once_with(
        query_embeddings=[[0.1, 0.2, 0.3]],
        n_results=4
    )


@patch("chat.engine.collection")
@patch("chat.engine.client")
def test_retrieve_respects_top_k(mock_client, mock_collection):
    """retrieve() should pass custom top_k to ChromaDB"""
    from chat.engine import retrieve

    mock_embedding = MagicMock()
    mock_embedding.embedding = [0.1]
    mock_client.embeddings.create.return_value = MagicMock(data=[mock_embedding])
    mock_collection.query.return_value = {"documents": [[]], "metadatas": [[]]}

    retrieve("test", top_k=2)
    mock_collection.query.assert_called_once_with(
        query_embeddings=[[0.1]],
        n_results=2
    )


# ========== chat() tests ==========

@patch("chat.engine.retrieve")
@patch("chat.engine.client")
def test_chat_returns_response_and_sources(mock_client, mock_retrieve):
    """chat() should return a dict with response and sources keys"""
    from chat.engine import chat, context_history
    context_history.clear()

    mock_retrieve.return_value = [
        {"document": "TFSA info here", "metadata": {"source": "rbc_tfsa.txt"}}
    ]

    mock_choice = MagicMock()
    mock_choice.message.content = "A TFSA is a tax-free savings account."
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

    result = chat("What is a TFSA?", "session-001")
    assert "response" in result
    assert "sources" in result
    assert result["response"] == "A TFSA is a tax-free savings account."
    assert len(result["sources"]) == 1


@patch("chat.engine.retrieve")
@patch("chat.engine.client")
def test_chat_uses_gpt4o_mini(mock_client, mock_retrieve):
    """chat() should call GPT-4o-mini"""
    from chat.engine import chat, context_history
    context_history.clear()

    mock_retrieve.return_value = [{"document": "text", "metadata": {"source": "f.txt"}}]
    mock_choice = MagicMock()
    mock_choice.message.content = "reply"
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

    chat("hello", "s1")
    call_args = mock_client.chat.completions.create.call_args
    assert call_args.kwargs["model"] == "gpt-4o-mini"
    assert call_args.kwargs["max_tokens"] == 500


@patch("chat.engine.retrieve")
@patch("chat.engine.client")
def test_chat_includes_system_prompt(mock_client, mock_retrieve):
    """chat() should include the system prompt in messages"""
    from chat.engine import chat, context_history, system_prompt
    context_history.clear()

    mock_retrieve.return_value = [{"document": "text", "metadata": {"source": "f.txt"}}]
    mock_choice = MagicMock()
    mock_choice.message.content = "reply"
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

    chat("hello", "s1")
    call_args = mock_client.chat.completions.create.call_args
    messages = call_args.kwargs["messages"]
    assert messages[0]["role"] == "system"
    assert system_prompt in messages[0]["content"]


@patch("chat.engine.retrieve")
@patch("chat.engine.client")
def test_chat_includes_context_in_system_message(mock_client, mock_retrieve):
    """chat() should inject retrieved context into the system message"""
    from chat.engine import chat, context_history
    context_history.clear()

    mock_retrieve.return_value = [
        {"document": "RBC TFSA has no monthly fee", "metadata": {"source": "rbc.txt"}}
    ]
    mock_choice = MagicMock()
    mock_choice.message.content = "reply"
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

    chat("TFSA fees?", "s1")
    call_args = mock_client.chat.completions.create.call_args
    system_msg = call_args.kwargs["messages"][0]["content"]
    assert "RBC TFSA has no monthly fee" in system_msg


# ========== Conversation history tests ==========

@patch("chat.engine.retrieve")
@patch("chat.engine.client")
def test_chat_stores_conversation_history(mock_client, mock_retrieve):
    """chat() should save user and assistant messages to context_history"""
    from chat.engine import chat, context_history
    context_history.clear()

    mock_retrieve.return_value = [{"document": "text", "metadata": {"source": "f.txt"}}]
    mock_choice = MagicMock()
    mock_choice.message.content = "I can help with that."
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

    chat("hello", "session-abc")

    assert "session-abc" in context_history
    assert len(context_history["session-abc"]) == 2  # user + assistant
    assert context_history["session-abc"][0]["role"] == "user"
    assert context_history["session-abc"][0]["content"] == "hello"
    assert context_history["session-abc"][1]["role"] == "assistant"
    assert context_history["session-abc"][1]["content"] == "I can help with that."


@patch("chat.engine.retrieve")
@patch("chat.engine.client")
def test_chat_maintains_separate_sessions(mock_client, mock_retrieve):
    """Different session_ids should have independent histories"""
    from chat.engine import chat, context_history
    context_history.clear()

    mock_retrieve.return_value = [{"document": "text", "metadata": {"source": "f.txt"}}]
    mock_choice = MagicMock()
    mock_choice.message.content = "reply"
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

    chat("question 1", "user-A")
    chat("question 2", "user-B")

    assert "user-A" in context_history
    assert "user-B" in context_history
    assert context_history["user-A"][0]["content"] == "question 1"
    assert context_history["user-B"][0]["content"] == "question 2"


@patch("chat.engine.retrieve")
@patch("chat.engine.client")
def test_chat_limits_history_to_6_messages(mock_client, mock_retrieve):
    """chat() should only send the last 6 messages to GPT"""
    from chat.engine import chat, context_history
    context_history.clear()

    mock_retrieve.return_value = [{"document": "text", "metadata": {"source": "f.txt"}}]
    mock_choice = MagicMock()
    mock_choice.message.content = "reply"
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

    # Send 5 messages to build up history
    for i in range(5):
        chat(f"message {i}", "long-session")

    call_args = mock_client.chat.completions.create.call_args
    messages = call_args.kwargs["messages"]
    # First message is system prompt, then at most 6 history messages
    non_system = [m for m in messages if m["role"] != "system"]
    assert len(non_system) <= 6


# ========== Data validation tests ==========

def test_system_prompt_exists():
    """system_prompt should be a non-empty string"""
    from chat.engine import system_prompt
    assert isinstance(system_prompt, str)
    assert len(system_prompt) > 50


def test_system_prompt_mentions_rbc():
    """system_prompt should reference RBC"""
    from chat.engine import system_prompt
    assert "RBC" in system_prompt


def test_system_prompt_warns_against_guessing():
    """system_prompt should instruct the bot not to make things up"""
    from chat.engine import system_prompt
    prompt_lower = system_prompt.lower()
    assert "never guess" in prompt_lower or "don't know" in prompt_lower or "never make up" in prompt_lower


def test_context_history_is_dict():
    """context_history should be a dictionary"""
    from chat.engine import context_history
    assert isinstance(context_history, dict)