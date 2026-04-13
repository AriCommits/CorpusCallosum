"""Tests for MCP server functionality."""

import pytest

from corpus_callosum.mcp_server import create_mcp_server


def test_create_mcp_server():
    """Test MCP server creation."""
    server = create_mcp_server()
    
    assert server is not None
    assert server.name == "Corpus Callosum"


def test_mcp_server_has_rag_tools():
    """Test that MCP server exposes RAG tools."""
    server = create_mcp_server()
    
    # Check that RAG tools are registered
    tool_names = [tool.name for tool in server.list_tools()]
    
    assert "rag_ingest" in tool_names
    assert "rag_query" in tool_names
    assert "rag_retrieve" in tool_names


def test_mcp_server_has_flashcard_tools():
    """Test that MCP server exposes flashcard tools."""
    server = create_mcp_server()
    
    tool_names = [tool.name for tool in server.list_tools()]
    
    assert "generate_flashcards" in tool_names


def test_mcp_server_has_summary_tools():
    """Test that MCP server exposes summary tools."""
    server = create_mcp_server()
    
    tool_names = [tool.name for tool in server.list_tools()]
    
    assert "generate_summary" in tool_names


def test_mcp_server_has_quiz_tools():
    """Test that MCP server exposes quiz tools."""
    server = create_mcp_server()
    
    tool_names = [tool.name for tool in server.list_tools()]
    
    assert "generate_quiz" in tool_names


def test_mcp_server_has_video_tools():
    """Test that MCP server exposes video tools."""
    server = create_mcp_server()
    
    tool_names = [tool.name for tool in server.list_tools()]
    
    assert "transcribe_video" in tool_names
    assert "clean_transcript" in tool_names


def test_mcp_server_has_resources():
    """Test that MCP server exposes resources."""
    server = create_mcp_server()
    
    resource_uris = [res.uri for res in server.list_resources()]
    
    assert "collections://list" in resource_uris


def test_mcp_server_has_prompts():
    """Test that MCP server exposes prompts."""
    server = create_mcp_server()
    
    prompt_names = [prompt.name for prompt in server.list_prompts()]
    
    assert "study_session_prompt" in prompt_names
    assert "lecture_processing_prompt" in prompt_names
