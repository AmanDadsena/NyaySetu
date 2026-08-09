"""
Analyze router — handles document upload and text analysis.
Accepts either raw text or file uploads (PDF, DOCX, TXT).

The analysis itself lives in `app.rag.document`, which prefers a locally running
model and falls back to a deterministic breakdown of the document. This router
is only responsible for getting text out of the upload and validating it.
"""

import io
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from app.rag.document import AnalysisResult, analyze_document, get_refinement

router = APIRouter(prefix="/api", tags=["analyze"])

# ── Allowed MIME types ──────────────────────────────────────────────────────
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}

MAX_FILE_SIZE_MB = 10


# ── Response models ─────────────────────────────────────────────────────────
# The result schema is defined alongside the analyser in app.rag.document so
# the model-facing schema and the API contract cannot drift apart.
class AnalyzeResponse(BaseModel):
    status: str
    data: AnalysisResult


class RefineResponse(BaseModel):
    #: ready | pending | gone — `gone` tells the client to stop polling.
    status: str
    data: Optional[AnalysisResult] = None


# ── Text extraction helpers ─────────────────────────────────────────────────
def _extract_text_from_pdf(content: bytes) -> str:
    """Extract text from PDF bytes using PyPDF2."""
    try:
        from PyPDF2 import PdfReader

        reader = PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages).strip()
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to extract text from PDF: {exc}",
        )


def _extract_text_from_docx(content: bytes) -> str:
    """Extract text from DOCX bytes using python-docx."""
    try:
        from docx import Document

        doc = Document(io.BytesIO(content))
        return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to extract text from DOCX: {exc}",
        )


def _extract_text_from_txt(content: bytes) -> str:
    """Decode plain-text bytes."""
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1")


# ── Endpoints ───────────────────────────────────────────────────────────────
@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_endpoint(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None),
    language: Optional[str] = Form("English"),
):
    """
    Analyze a legal document using AI. Accepts **either**:
    - `file`: an uploaded PDF, DOCX, or TXT file
    - `raw_text`: pasted plain text
    Also accepts:
    - `language`: output language (e.g., 'Hindi', 'Marathi')
    """

    text = ""

    # ── Handle file upload ──────────────────────────────────────────────
    if file is not None:
        # Validate content type
        content_type = file.content_type or ""
        if content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {content_type}. Allowed: PDF, DOCX, TXT.",
            )

        content = await file.read()

        # Validate size
        if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB} MB.",
            )

        # Extract text based on type
        if content_type == "application/pdf":
            text = _extract_text_from_pdf(content)
        elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = _extract_text_from_docx(content)
        else:
            text = _extract_text_from_txt(content)

    # ── Handle raw text ─────────────────────────────────────────────────
    elif raw_text is not None and raw_text.strip():
        text = raw_text.strip()

    else:
        raise HTTPException(
            status_code=400,
            detail="No input provided. Please upload a file or paste text.",
        )

    if len(text) < 20:
        raise HTTPException(
            status_code=400,
            detail="Text is too short for meaningful analysis. Please provide more content.",
        )

    # ── Analyze ─────────────────────────────────────────────────────────
    result = await analyze_document(text, language or "English")
    return AnalyzeResponse(status="success", data=result)


@router.get("/analyze/refine/{refine_id}", response_model=RefineResponse)
async def analyze_refine(refine_id: str) -> RefineResponse:
    """
    Poll for the model-enriched version of an analysis already delivered.

    The first response to /api/analyze is the deterministic breakdown, returned
    in well under a second. A local model then rewrites the summary, clause
    explanations and next steps behind it; the client swaps them in when this
    endpoint reports `ready`, and stops polling on `gone`.
    """
    status, result = await get_refinement(refine_id)
    return RefineResponse(status=status, data=result)
