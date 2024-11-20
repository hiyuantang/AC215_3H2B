from fastapi import APIRouter, Header, HTTPException
from typing import Optional
import uuid
import time
from api.utils.llm_utils import generate_chat_response, prepare_response
from api.utils.chat_utils import ChatHistoryManager
from api.utils.input_base import UserInput

# Define Router
router = APIRouter()

# Initialize chat history manager and sessions
chat_manager = ChatHistoryManager(model="tripee")

@router.get("/chats")
async def get_chats(x_session_id: str = Header(None, alias="X-Session-ID"), limit: Optional[int] = None):
    """Get all chats, optionally limited to a specific number"""
    print("x_session_id:", x_session_id)
    return chat_manager.get_recent_chats(x_session_id, limit)

@router.get("/chats/{chat_id}")
async def get_chat(chat_id: str, x_session_id: str = Header(None, alias="X-Session-ID")):
    """Get a specific chat by ID"""
    print("x_session_id:", x_session_id)
    chat = chat_manager.get_chat(chat_id, x_session_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat

@router.post("/chats")
async def start_chat_with_llm(input_data: UserInput, x_session_id: str = Header(None, alias="X-Session-ID")):
    print("content:", input_data.city, input_data.days, input_data.type, input_data.month)
    print("x_session_id:", x_session_id)
    """Start a new chat with an initial message"""
    chat_id = str(uuid.uuid4())
    current_time = int(time.time())
    
    # Add ID and role to the user message
    input_data.message_id = str(uuid.uuid4())
    input_data.role = "user"
    
    # Get and prepare LLM response
    max_tries = 5
    tries = 0
    title = None
    travel_iti = None

    while tries < max_tries:
        llm_sf_response = generate_chat_response(input_data)
        try:
            title, travel_iti, themes = prepare_response(llm_sf_response)
            if title is not None and travel_iti is not None:
                break  # Exit the loop if both title and travel_iti are valid
        except Exception as e:
            print(f"An error occurred in prepare_response: {e}")
        tries += 1

    if title is None or travel_iti is None:
        print("Failed to get valid 'title' and 'travel_iti' after 3 attempts.")
    else:
        print("Title and travel itinerary obtained successfully.")
    
    # Create chat response
    iti_first_draft = {
        "chat_id": chat_id,
        "title": title,
        "dts": current_time,
        "messages": [
            {
                "city": input_data.city,
                "days": input_data.days,
                "type": input_data.type,
                "month": input_data.month
            }, 
            {
                "message_id": str(uuid.uuid4()),
                "kind": "sf_response",
                "days_locations": travel_iti, 
                "days_themes": themes
            }
        ]
    }
    
    # Save chat
    chat_manager.save_chat(iti_first_draft, x_session_id)
    return iti_first_draft