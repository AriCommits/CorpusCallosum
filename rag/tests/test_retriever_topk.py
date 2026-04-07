"""Tests for dynamic top_k parameter in retriever."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from corpus_callosum.retriever import HybridRetriever, RetrievedChunk


@pytest.fixture
def mock_config():
    """Create a mock config."""
    config = Mock()
    config.retrieval.top_k_semantic = 10
    config.retrieval.top_k_bm25 = 10
    config.retrieval.top_k_final = 5
    config.retrieval.rrf_k = 60
    return config


@pytest.fixture
def mock_chroma_client():
    """Create a mock ChromaDB client."""
    return MagicMock()


@pytest.fixture
def mock_embedding_backend():
    """Create a mock embedding backend."""
    backend = Mock()
    backend.encode = Mock(return_value=[[0.1, 0.2, 0.3]])
    return backend


def test_retriever_semantic_search_default_k(mock_config, mock_chroma_client, mock_embedding_backend):
    """Test semantic search with default top_k from config."""
    # Setup mock collection
    collection = Mock()
    collection.count = Mock(return_value=15)
    collection.query = Mock(
        return_value={
            "ids": [["doc1", "doc2", "doc3"]],
            "documents": [["Text 1", "Text 2", "Text 3"]],
            "metadatas": [[{}, {}, {}]],
        }
    )
    mock_chroma_client.get_collection = Mock(return_value=collection)

    retriever = HybridRetriever(
        config=mock_config,
        chroma_client=mock_chroma_client,
        embedding_backend=mock_embedding_backend,
    )

    results = retriever.semantic_search(query="test query", collection_name="test")

    # Verify it used the default top_k from config
    assert collection.query.called
    call_args = collection.query.call_args
    assert call_args[1]["n_results"] == 10  # Default from config


def test_retriever_semantic_search_custom_k(mock_config, mock_chroma_client, mock_embedding_backend):
    """Test semantic search with custom top_k parameter."""
    # Setup mock collection
    collection = Mock()
    collection.count = Mock(return_value=15)
    collection.query = Mock(
        return_value={
            "ids": [["doc1", "doc2"]],
            "documents": [["Text 1", "Text 2"]],
            "metadatas": [[{}, {}]],
        }
    )
    mock_chroma_client.get_collection = Mock(return_value=collection)

    retriever = HybridRetriever(
        config=mock_config,
        chroma_client=mock_chroma_client,
        embedding_backend=mock_embedding_backend,
    )

    # Use custom top_k
    results = retriever.semantic_search(query="test query", collection_name="test", top_k=2)

    # Verify it used the custom top_k
    assert collection.query.called
    call_args = collection.query.call_args
    assert call_args[1]["n_results"] == 2  # Custom value


def test_retriever_bm25_search_custom_k(mock_config, mock_chroma_client):
    """Test BM25 search with custom top_k parameter."""
    # Setup mock collection
    collection = Mock()
    collection.get = Mock(
        return_value={
            "ids": ["doc1", "doc2", "doc3", "doc4", "doc5"],
            "documents": [
                "test document one",
                "test document two",
                "another document",
                "more test content",
                "final document",
            ],
            "metadatas": [{}, {}, {}, {}, {}],
        }
    )
    mock_chroma_client.get_collection = Mock(return_value=collection)

    retriever = HybridRetriever(config=mock_config, chroma_client=mock_chroma_client)

    # Use custom top_k=3
    results = retriever.bm25_search(query="test", collection_name="test", top_k=3)

    # Should return at most 3 results
    assert len(results) <= 3


def test_retriever_retrieve_custom_k(mock_config, mock_chroma_client, mock_embedding_backend):
    """Test full retrieve() method with custom top_k."""
    # Setup mock collection
    collection = Mock()
    collection.count = Mock(return_value=10)
    collection.query = Mock(
        return_value={
            "ids": [["doc1", "doc2"]],
            "documents": [["Text 1", "Text 2"]],
            "metadatas": [[{}, {}]],
        }
    )
    collection.get = Mock(
        return_value={
            "ids": ["doc1", "doc2", "doc3"],
            "documents": ["Text 1", "Text 2", "Text 3"],
            "metadatas": [{}, {}, {}],
        }
    )
    mock_chroma_client.get_collection = Mock(return_value=collection)

    retriever = HybridRetriever(
        config=mock_config,
        chroma_client=mock_chroma_client,
        embedding_backend=mock_embedding_backend,
    )

    # Use custom top_k=2
    results = retriever.retrieve(query="test query", collection_name="test", top_k=2)

    # Should return at most 2 results after RRF
    assert len(results) <= 2


def test_retriever_retrieve_respects_final_k(mock_config, mock_chroma_client, mock_embedding_backend):
    """Test that retrieve() respects top_k for final results."""
    # Setup mock collection with many results
    all_ids = [f"doc{i}" for i in range(20)]
    all_texts = [f"Text {i}" for i in range(20)]
    all_metas = [{} for _ in range(20)]

    collection = Mock()
    collection.count = Mock(return_value=20)
    collection.query = Mock(
        return_value={
            "ids": [all_ids[:10]],
            "documents": [all_texts[:10]],
            "metadatas": [all_metas[:10]],
        }
    )
    collection.get = Mock(
        return_value={
            "ids": all_ids,
            "documents": all_texts,
            "metadatas": all_metas,
        }
    )
    mock_chroma_client.get_collection = Mock(return_value=collection)

    retriever = HybridRetriever(
        config=mock_config,
        chroma_client=mock_chroma_client,
        embedding_backend=mock_embedding_backend,
    )

    # Request exactly 7 results
    results = retriever.retrieve(query="test", collection_name="test", top_k=7)

    # Should get exactly 7 (or fewer if not enough matches)
    assert len(results) <= 7


@pytest.mark.parametrize("top_k_value", [1, 5, 10, 20, 100])
def test_retriever_various_k_values(
    top_k_value, mock_config, mock_chroma_client, mock_embedding_backend
):
    """Test retriever with various top_k values."""
    # Setup mock collection
    collection = Mock()
    collection.count = Mock(return_value=100)
    collection.query = Mock(
        return_value={
            "ids": [[f"doc{i}" for i in range(min(top_k_value, 100))]],
            "documents": [[f"Text {i}" for i in range(min(top_k_value, 100))]],
            "metadatas": [[{} for _ in range(min(top_k_value, 100))]],
        }
    )
    collection.get = Mock(
        return_value={
            "ids": [f"doc{i}" for i in range(100)],
            "documents": [f"Text {i}" for i in range(100)],
            "metadatas": [{} for _ in range(100)],
        }
    )
    mock_chroma_client.get_collection = Mock(return_value=collection)

    retriever = HybridRetriever(
        config=mock_config,
        chroma_client=mock_chroma_client,
        embedding_backend=mock_embedding_backend,
    )

    results = retriever.retrieve(query="test", collection_name="test", top_k=top_k_value)

    # Should return at most top_k_value results
    assert len(results) <= top_k_value
