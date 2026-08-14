"""
Chat endpoint for the Nyaysetu legal assistant.

Answers are retrieval-grounded: the question is matched against a curated corpus
of Indian statute passages (`app.rag.corpus`), and only that material is used to
compose the reply. The generation step is optional and falls back through a
local model, then a hosted one, then a purely extractive answer — so the
assistant keeps working with no API key at all.

This replaced an earlier keyword-matched FAQ table. The corpus is now the single
source of truth for legal content; add a passage there to teach a new topic.
"""

from typing import List, Optional

import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.rag import answer_question
from app.rag import feedback
from app.rag.engine import stream_answer

router = APIRouter(prefix="/api/bot", tags=["bot"])


class ChatMessage(BaseModel):
    role: str  # "user" or "model"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []
    # Plain-English language name (e.g. "Hindi", "Tamil"). The frontend sends
    # this from the global locale picker; older clients omit it.
    language: str = "English"
    # Corpus passage id, when the user tapped a suggested question rather than
    # typing. The chips are translated, so pinning by id keeps them accurate
    # in every script without the corpus needing translations of its own.
    topic: Optional[str] = None
    # Random value the client keeps for the life of one conversation. Used only
    # to tell "asked again, differently" from "asked something new" — it maps to
    # no account and is never stored alongside one. See app/rag/feedback.py.
    session: Optional[str] = None


class SourceRef(BaseModel):
    #: Corpus passage id, so the client can pull the exact text behind a claim.
    id: str = ""
    title: str
    citation: str
    url: str


class ChatResponse(BaseModel):
    status: str
    reply: str
    #: Statute passages the answer was grounded in, for the citations UI.
    sources: List[SourceRef] = []
    #: Which generator wrote the prose: ollama | gemini | extractive | none.
    provider: str = "none"
    #: How well the corpus covered the question: high | medium | none.
    grounding: str = "none"


@router.post("/chat", response_model=ChatResponse)
async def bot_chat(request: ChatRequest) -> ChatResponse:
    answer = await answer_question(
        question=request.message,
        language=request.language,
        topic=request.topic,
    )

    feedback.record(
        question=request.message,
        retrieved=[s.id for s in answer.sources],
        top_score=answer.sources[0].score if answer.sources else 0.0,
        grounding=answer.grounding,
        language=request.language,
        session=request.session,
    )

    return ChatResponse(
        status="success",
        reply=answer.reply,
        sources=[
            SourceRef(id=s.id, title=s.title, citation=s.citation, url=s.url)
            for s in answer.sources
        ],
        provider=answer.provider,
        grounding=answer.grounding,
    )


@router.get("/passage/{passage_id}")
async def get_passage(passage_id: str) -> dict:
    """
    The exact text an answer was built from.

    A citation the reader cannot check is a claim, not a citation. Most of the
    corpus cites India Code, whose `source_url` is a portal front page — it
    proves the Act exists, not that it says what the answer says it says. This
    returns the passage itself so the reader can compare the two.
    """
    from app.rag.corpus import get as get_passage_by_id

    passage = get_passage_by_id(passage_id)
    if passage is None:
        raise HTTPException(status_code=404, detail=f"Unknown passage: {passage_id}")

    return {
        "id": passage.id,
        "title": passage.title,
        "act": passage.act,
        "section": passage.section,
        "citation": passage.citation,
        "text": passage.text,
        "url": passage.source_url,
        "topics": list(passage.topics),
        "also_known_as": list(passage.also_known_as),
    }


@router.get("/health")
async def bot_health() -> dict:
    """
    Report which answering capabilities this deployment actually has.

    Useful when demoing: it distinguishes "no model configured, answering
    extractively" from "something is broken".
    """
    from app.rag.corpus import CORPUS
    from app.rag.retriever import get_retriever

    retriever = get_retriever()
    return {
        "passages": len(CORPUS),
        "dense_retrieval": retriever.dense.available,
        "status": "ready",
    }


@router.post("/chat/stream")
async def bot_chat_stream(request: ChatRequest) -> StreamingResponse:
    """
    Server-sent events version of /chat.

    Emits the citations first, then the reply token by token. Time-to-first-word
    drops to about a second even on a model that needs a minute to finish, which
    is the difference between the assistant feeling broken and feeling fast.
    """

    async def events():
        try:
            async for event in stream_answer(
                question=request.message,
                language=request.language,
                topic=request.topic,
            ):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as exc:  # never leave the client hanging on the stream
            print(f"[bot] stream error: {exc}")
            yield f"data: {json.dumps({'type': 'done', 'provider': 'none'})}\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            # Proxies that buffer would defeat the entire point of streaming.
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
