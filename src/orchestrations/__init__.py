"""
Orchestrations for Corpus Callosum.

Pre-composed workflows that combine multiple tools for common use cases.
"""

from .study_session import StudySessionOrchestrator
from .lecture_pipeline import LecturePipelineOrchestrator
from .knowledge_base import KnowledgeBaseOrchestrator

__all__ = [
    "StudySessionOrchestrator",
    "LecturePipelineOrchestrator",
    "KnowledgeBaseOrchestrator",
]
