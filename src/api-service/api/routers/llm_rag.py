import os
import json
from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from api.utils.llm_rag_utils import generate_chat_response
from api.utils.chat_utils import ChatHistoryManager

# Define Router
router = APIRouter()

# Initialize chat history manager and sessions
chat_manager = ChatHistoryManager(model="tripee")


@router.get("/plans")
async def get_plans(
    x_session_id: str = Header(None, alias="X-Session-ID"), limit: Optional[int] = None
):
    """Get all plans, optionally limited to a specific number"""
    print("x_session_id:", x_session_id)
    return chat_manager.get_recent_chats(x_session_id, limit)


@router.get("/plans/{chat_id}")
async def get_plan(
    chat_id: str, x_session_id: str = Header(None, alias="X-Session-ID")
):
    """Get a specific chat by ID"""
    print("x_session_id:", x_session_id)
    print("chat_id:", chat_id)

    chat = chat_manager.get_chat(chat_id, x_session_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.post("/plans/{chat_id}")
async def post_plan(
    chat_id: str, x_session_id: str = Header(None, alias="X-Session-ID")
):
    print("x_session_id:", x_session_id)
    print("chat_id:", chat_id)

    # Construct the file path
    file_path = f"chat-history/tripee/{x_session_id}/{chat_id}.json"

    # Check if the file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Chat file not found")

    # Read and parse the JSON file
    try:
        with open(file_path, "r") as file:
            iti_reorder = json.load(file)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")

    title = iti_reorder["title"]
    ordered_locations = iti_reorder["messages"][2]["ordered_locations"]
    days_themes = iti_reorder["messages"][1]["days_themes"]

    # Generate response
    final_iti = generate_chat_response(title, ordered_locations, days_themes)
    final_iti = {"final_iti": final_iti}
    iti_reorder["messages"].append(final_iti)

    # Save the updated JSON back to the file
    try:
        with open(file_path, "w") as file:
            json.dump(iti_reorder, file, indent=2, ensure_ascii=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {e}")

    print(final_iti)

    return final_iti
