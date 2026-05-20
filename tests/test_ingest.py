# tests/test_ingest.py
import pytest
from unittest.mock import patch, MagicMock
import os

from rag.ingest import chunk


# ========== chunk() — white box tests ==========

def test_chunk_returns_list():
    """chunk() should return a list of strings"""
    result = chunk("word " * 100)
    assert isinstance(result, list)
    assert all(isinstance(c, str) for c in result)


def test_chunk_single_chunk_for_short_text():
    """Text shorter than chunk size should return exactly one chunk"""
    text = "hello world this is a short sentence"
    result = chunk(text, size=400, overlap=50)
    assert len(result) == 1
    assert result[0] == text


def test_chunk_splits_long_text():
    """Text longer than chunk size should produce multiple chunks"""
    text = " ".join([f"word{i}" for i in range(800)])
    result = chunk(text, size=400, overlap=50)
    assert len(result) > 1


def test_chunk_respects_size():
    """Each chunk should have at most 'size' words"""
    text = " ".join([f"word{i}" for i in range(1000)])
    result = chunk(text, size=400, overlap=50)
    for c in result:
        assert len(c.split()) <= 400


def test_chunk_overlap_creates_shared_words():
    """Consecutive chunks should share 'overlap' words"""
    text = " ".join([f"word{i}" for i in range(800)])
    result = chunk(text, size=400, overlap=50)
    first_chunk_words = result[0].split()
    second_chunk_words = result[1].split()
    # Last 50 words of chunk 1 should equal first 50 words of chunk 2
    assert first_chunk_words[-50:] == second_chunk_words[:50]


def test_chunk_empty_string():
    """Empty string should return a single empty chunk"""
    result = chunk("")
    assert result == []


def test_chunk_exact_size():
    """Text with exactly 'size' words should return one chunk"""
    text = " ".join([f"word{i}" for i in range(400)])
    result = chunk(text, size=400, overlap=50)
    assert len(result) == 2
    assert len(result[0].split()) == 400


def test_chunk_custom_size_and_overlap():
    """chunk() should respect custom size and overlap parameters"""
    text = " ".join([f"w{i}" for i in range(200)])
    result = chunk(text, size=100, overlap=20)
    assert len(result) > 1
    for c in result:
        assert len(c.split()) <= 100


def test_chunk_covers_all_words():
    """No words should be lost — every word in the original should appear in at least one chunk"""
    words = [f"word{i}" for i in range(500)]
    text = " ".join(words)
    result = chunk(text, size=400, overlap=50)
    all_chunk_words = set()
    for c in result:
        all_chunk_words.update(c.split())
    for w in words:
        assert w in all_chunk_words


# ========== embed() — mocked tests ==========

@patch("rag.ingest.client")
def test_embed_returns_list_of_vectors(mock_client):
    """embed() should return a list of embedding vectors"""
    from rag.ingest import embed

    # Mock the OpenAI response
    mock_embedding = MagicMock()
    mock_embedding.embedding = [0.1, 0.2, 0.3]
    mock_client.embeddings.create.return_value = MagicMock(data=[mock_embedding, mock_embedding])

    result = embed(["hello", "world"])
    assert len(result) == 2
    assert result[0] == [0.1, 0.2, 0.3]


@patch("rag.ingest.client")
def test_embed_calls_openai_with_correct_model(mock_client):
    """embed() should use text-embedding-3-small model"""
    from rag.ingest import embed

    mock_client.embeddings.create.return_value = MagicMock(data=[])
    embed(["test"])
    mock_client.embeddings.create.assert_called_once_with(
        input=["test"], model="text-embedding-3-small"
    )


# ========== ingest_all() — mocked tests ==========

@patch("rag.ingest.collection")
@patch("rag.ingest.embed")
@patch("rag.ingest.chunk")
@patch("builtins.open", create=True)
@patch("os.listdir")
def test_ingest_all_processes_files(mock_listdir, mock_open, mock_chunk, mock_embed, mock_collection):
    """ingest_all() should read files, chunk, embed, and store them"""
    from rag.ingest import ingest_all

    # Setup mocks
    mock_listdir.return_value = ["rbc_chequing.txt"]
    mock_open.return_value.__enter__ = lambda s: s
    mock_open.return_value.__exit__ = MagicMock(return_value=False)
    mock_open.return_value.read.return_value = "some banking text here"
    mock_chunk.return_value = ["chunk1", "chunk2"]
    mock_embed.return_value = [[0.1, 0.2], [0.3, 0.4]]

    ingest_all()

    # Verify the pipeline ran
    mock_chunk.assert_called_once_with("some banking text here")
    mock_embed.assert_called_once_with(["chunk1", "chunk2"])
    mock_collection.add.assert_called_once()


@patch("rag.ingest.collection")
@patch("rag.ingest.embed")
@patch("rag.ingest.chunk")
@patch("builtins.open", create=True)
@patch("os.listdir")
def test_ingest_all_generates_correct_ids(mock_listdir, mock_open, mock_chunk, mock_embed, mock_collection):
    """ingest_all() should generate unique IDs per chunk"""
    from rag.ingest import ingest_all

    mock_listdir.return_value = ["test_file.txt"]
    mock_open.return_value.__enter__ = lambda s: s
    mock_open.return_value.__exit__ = MagicMock(return_value=False)
    mock_open.return_value.read.return_value = "text"
    mock_chunk.return_value = ["c1", "c2", "c3"]
    mock_embed.return_value = [[0.1], [0.2], [0.3]]

    ingest_all()

    call_args = mock_collection.add.call_args
    ids = call_args.kwargs.get("ids") or call_args[1].get("ids")
    assert ids == ["test_file.txt_0", "test_file.txt_1", "test_file.txt_2"]