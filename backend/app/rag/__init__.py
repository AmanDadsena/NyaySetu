"""
Retrieval-augmented answering over a curated corpus of Indian law.

The point of this package is that Nyaysetu answers legal questions without
depending on any hosted AI service. Retrieval always runs locally; generation
is optional and degrades in this order:

    local LLM (Ollama)  ->  hosted model (Gemini)  ->  extractive answer

The last step composes a reply directly from the retrieved statute passages,
so the assistant keeps working with no API key, no GPU and no network.
"""

from .corpus import CORPUS, Passage
from .engine import LegalAnswer, answer_question
from .retriever import RetrievedPassage, get_retriever

__all__ = [
    "CORPUS",
    "Passage",
    "LegalAnswer",
    "RetrievedPassage",
    "answer_question",
    "get_retriever",
]
