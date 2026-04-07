"""RAG agent orchestration."""

from typing import Iterator, Optional

from corpus_callosum.db import DatabaseBackend

from .config import RAGConfig
from .retriever import RAGRetriever, RetrievedChunk


class RAGAgent:
    """RAG agent for retrieval-augmented generation."""

    def __init__(self, config: RAGConfig, db: DatabaseBackend):
        """Initialize RAG agent.

        Args:
            config: RAG configuration
            db: Database backend
        """
        self.config = config
        self.db = db
        self.retriever = RAGRetriever(config, db)

    def query(
        self,
        query: str,
        collection: str,
        top_k: Optional[int] = None,
        stream: bool = False,
    ) -> tuple[str | Iterator[str], list[RetrievedChunk]]:
        """Execute RAG query.

        Args:
            query: User query
            collection: Collection name to search
            top_k: Number of documents to retrieve
            stream: Whether to stream the response

        Returns:
            Tuple of (response text or iterator, retrieved chunks)
        """
        # Retrieve relevant chunks
        chunks = self.retriever.retrieve(query, collection, top_k)

        # Build prompt with context
        prompt = self._build_rag_prompt(query, chunks)

        # Generate response (placeholder - will be implemented with LLM backend)
        # In full implementation, this would:
        # 1. Call the LLM backend with the prompt
        # 2. Stream or return complete response
        # 3. Handle conversation history if needed
        
        response = f"[RAG Response Placeholder]\nQuery: {query}\nRetrieved {len(chunks)} chunks from {collection}"
        
        if stream:
            def response_generator():
                yield response
            return response_generator(), chunks
        else:
            return response, chunks

    def _build_rag_prompt(self, query: str, chunks: list[RetrievedChunk]) -> str:
        """Build RAG prompt with retrieved context.

        Args:
            query: User query
            chunks: Retrieved document chunks

        Returns:
            Formatted prompt string
        """
        if not chunks:
            return query

        # Build context from chunks
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk.metadata.get("source_file", "unknown")
            context_parts.append(f"[{i}] (from {source}):\n{chunk.text}")

        context = "\n\n".join(context_parts)

        # Format final prompt
        prompt = f"""Answer the following question using the provided context.

Context:
{context}

Question: {query}

Answer:"""

        return prompt

    def chat(
        self,
        message: str,
        collection: str,
        session_id: Optional[str] = None,
        stream: bool = False,
    ) -> str | Iterator[str]:
        """Chat with RAG agent maintaining conversation history.

        Args:
            message: User message
            collection: Collection name to search
            session_id: Optional session ID for conversation history
            stream: Whether to stream the response

        Returns:
            Response text or iterator
        """
        # Placeholder for chat with history
        # Full implementation would:
        # 1. Load conversation history from session_id
        # 2. Retrieve relevant chunks
        # 3. Build prompt with history + chunks
        # 4. Generate response
        # 5. Save to conversation history
        
        response, _ = self.query(message, collection, stream=stream)
        return response
