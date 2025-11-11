from google import genai
from google.genai import types
from typing import List, Dict, Optional
from pydantic import BaseModel
from db import chats_collection
from datetime import datetime

client = genai.Client()  # reads GEMINI_API_KEY from env

conversation_history: Dict[str, List[str]] = {}
DEFAULT_SESSION_ID = "global_session"

# --- Pydantic Models ---
class CareerRecommendation(BaseModel):
    title: str
    matchPercentage: int

class ChatRequest(BaseModel):
    message: str
    recommendations: Optional[List[CareerRecommendation]] = None
    sessionId: str = DEFAULT_SESSION_ID

class ChatResponse(BaseModel):
    response: str

# --- Helper to store messages ---
def save_message(user_id: str, session_id: str, role: str, message: str):
    chats_collection.insert_one({
        "userId": user_id,
        "sessionId": session_id,
        "role": role,
        "message": message,
        "timestamp": datetime.utcnow()
    })

# --- Main chatbot function ---
def get_chat_response(req: ChatRequest, user_id: str) -> ChatResponse:
    try:
        # Initialize conversation history
        if req.sessionId not in conversation_history:
            conversation_history[req.sessionId] = []

        # Save user message
        save_message(user_id, req.sessionId, "user", req.message)
        conversation_history[req.sessionId].append(req.message)

        # Load last 10 messages for context
        prev_msgs_cursor = chats_collection.find(
            {"userId": user_id, "sessionId": req.sessionId}
        ).sort("timestamp", 1)
        prev_msgs = list(prev_msgs_cursor)[-10:]
        context_text = "\n".join([f"{m['role']}: {m['message']}" for m in prev_msgs])

        # Build system prompt
        system_prompt = (
            "You are a friendly career guidance chatbot named 'Pathly'. "
            "Help users explore career paths based on their interests and assessment results. "
            "Be concise, helpful, and positive."
        )
        if req.recommendations:
            recs = ", ".join([f"{r.title} ({r.matchPercentage}% match)" for r in req.recommendations])
            system_prompt += f" The user's top career recommendations are: {recs}."
        if context_text:
            system_prompt += "\nPrevious conversation:\n" + context_text

        # Call Gemini API
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=req.message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt
            )
        )

        assistant_text = response.text
        # Save assistant message
        save_message(user_id, req.sessionId, "assistant", assistant_text)

        return ChatResponse(response=assistant_text)

    except Exception:
        return ChatResponse(response="Chatbot is temporarily unavailable due to API limits. Please try again later.")