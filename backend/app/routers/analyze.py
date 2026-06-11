"""
Analyze router — handles document upload and text analysis.
Accepts either raw text or file uploads (PDF, DOCX, TXT).
Returns structured legal-document analysis using Google GenAI (Gemini).
"""

import io
import os
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from google import genai

router = APIRouter(prefix="/api", tags=["analyze"])

# ── Allowed MIME types ──────────────────────────────────────────────────────
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}

MAX_FILE_SIZE_MB = 10


# ── Response models ─────────────────────────────────────────────────────────
class ClauseItem(BaseModel):
    title: str
    content: str
    risk_level: str  # "low" | "medium" | "high"


class AnalysisResult(BaseModel):
    summary: str
    document_type: str
    word_count: int
    char_count: int
    clauses: list[ClauseItem]
    key_entities: list[str]
    risk_flags: list[str]
    recommendations: list[str]


class AnalyzeResponse(BaseModel):
    status: str
    data: AnalysisResult


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


# ── Gemini Engine ───────────────────────────────────────────────────────────
def _analyze_legal_text(raw_text: str, language: str) -> AnalysisResult:
    """
    Perform AI analysis on the legal text using Google Gemini 2.5 Flash.
    Instructs the AI to translate and explain the output in the target language.
    """
    words = raw_text.split()
    word_count = len(words)
    char_count = len(raw_text)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured in the backend environment.",
        )

    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are an expert, highly experienced legal analyst, legal scholar, and bilingual translator. 
    Analyze the following legal document with extreme accuracy and provide a highly detailed, easy-to-understand breakdown.
    
    CRITICAL INSTRUCTIONS:
    1. EXTREME ACCURACY: Ensure your legal interpretations are perfectly sound, factually accurate, and contextually appropriate. Do not hallucinate laws.
    2. SOURCES & REFERENCES: You MUST cite specific sections of laws, acts (e.g., Bharatiya Nyaya Sanhita, Indian Penal Code, Indian Contract Act, Motor Vehicles Act), precedents, or relevant legal doctrines to back up every point in your analysis. Provide the exact source.
    3. DETAILED & SIMPLIFIED EXPLANATION: Break down complex legal jargon into plain, easy-to-understand language so a layperson can fully comprehend their rights and obligations. Provide IN-DEPTH explanations for every clause and risk.
    4. LANGUAGE: Provide your ENTIRE explanation, summary, extracted clauses, risk flags, and recommendations completely in {language}. Do not use English unless the user's language is English or it's a specific legal term that cannot be translated.

    Follow the structured JSON output format exactly. 
    - In your 'summary', provide a comprehensive, step-by-step overview of the document, explaining its legal significance, and explicitly citing all relevant laws or sources.
    - Extract key clauses, determine their risk level ('low', 'medium', 'high'). For the 'content' field of each clause, provide a VERY detailed explanation of what it means, why it matters, and cite the exact legal sources and acts that govern it.
    - Identify critical entities (like people or companies).
    - List any risk flags with detailed legal reasoning, citing exact sources, and explaining potential consequences.
    - Provide clear, actionable recommendations backed by in-depth legal rationale and exact sources.

    --- DOCUMENT TEXT ---
    {raw_text}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=prompt,
            config={
                'response_mime_type': 'application/json',
                'response_schema': AnalysisResult,
                'temperature': 0.1,
            },
        )
        
        # Pydantic will validate the JSON string returned by Gemini.
        result = AnalysisResult.model_validate_json(response.text)
        
        # Override the word/char counts with accurate deterministic counts.
        result.word_count = word_count
        result.char_count = char_count
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI Analysis failed: {str(e)}",
        )


# ── Endpoints ───────────────────────────────────────────────────────────────
@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_document(
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
    result = _analyze_legal_text(text, language)
    return AnalyzeResponse(status="success", data=result)
