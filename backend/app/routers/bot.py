import os
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types

router = APIRouter(prefix="/api/bot", tags=["bot"])

class ChatMessage(BaseModel):
    role: str  # "user" or "model"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []

class ChatResponse(BaseModel):
    status: str
    reply: str

@router.post("/chat", response_model=ChatResponse)
async def bot_chat(request: ChatRequest):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your_api_key_here":
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is not configured in the backend environment."
        )

    try:
        client = genai.Client(api_key=api_key)
        
        system_instruction = """
You are the Nyaysetu AI Assistant, a friendly, professional, and accessible legal guide for the Nyaysetu website.
Your primary role is to help users navigate the website and answer basic legal FAQs accurately according to Indian law.

Key responsibilities:
1. Guide users through the platform features (Analyze Documents, Find Lawyers, Case Tracking, Legal Knowledge).
2. Answer frequently asked legal questions simply and clearly, referencing official Indian legal sources (like NALSA, the Constitution, BNS, IPC) when applicable.
3. Keep your answers concise, accessible to laypersons, and highly accurate. Do NOT hallucinate laws.
4. If a user asks for formal legal advice, remind them that you provide legal information, not formal legal counsel, and direct them to the "Find Lawyers" section.
5. Provide your answers in standard Markdown format (using bolding, bullets, and short paragraphs) so it renders well in the chat UI.
"""

        # Convert history into the format expected by the Google GenAI SDK
        contents = []
        for msg in request.history:
            role = "user" if msg.role == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(msg.content)]))
        
        # Add the new message
        contents.append(types.Content(role="user", parts=[types.Part.from_text(request.message)]))

        response = client.models.generate_content(
            model='gemini-2.5-pro',
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3,
            ),
        )
        
        return ChatResponse(status="success", reply=response.text)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI Chat failed: {str(e)}"
        )
