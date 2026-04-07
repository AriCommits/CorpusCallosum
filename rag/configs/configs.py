from pydantic_settings import BaseSettings
from pydantic import BaseModel

class LLMSettings(BaseModel):
    endpoint: str = "http://localhost:11434"
    model: str = "llama3"
    max_tokens: int = 2048
    temperature: float = 0.7
    timeout_seconds: float = 120.0

class RetrievalSettings(BaseModel):
    top_k_final: int = 10
    bm25_weight: float = 0.3
    semantic_weight: float = 0.7

class ChunkingSettings(BaseModel):
    size: int = 1000
    overlap: int = 100

class Settings(BaseSettings):
    llm: LLMSettings = LLMSettings()
    retrieval: RetrievalSettings = RetrievalSettings()
    chunking: ChunkingSettings = ChunkingSettings()
    # ... rest of your existing config sections

    model_config = {"yaml_file": "configs/corpus_callosum.yaml"}