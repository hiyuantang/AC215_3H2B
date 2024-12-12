import os
import json
from fastapi import APIRouter, Header, HTTPException
from api.utils.optimize_utils import get_reranked_locations_all

# Define Router
router = APIRouter()


@router.post("/loc_coord/{chat_id}")
async def post_coord_from_chat(
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
            iti_first_draft = json.load(file)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")

    print("x_session_id:", x_session_id)
    print("chat_id:", iti_first_draft["chat_id"])
    print("title:", iti_first_draft["title"])

    ordered_locations, ordered_coordinates = get_reranked_locations_all(iti_first_draft)

    iti_first_draft["messages"].append(
        {
            "ordered_locations": ordered_locations,
            "ordered_coordinates": ordered_coordinates,
        }
    )

    # Save the updated JSON back to the file
    try:
        with open(file_path, "w") as file:
            json.dump(iti_first_draft, file, indent=2, ensure_ascii=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {e}")

    return {
        "ordered_locations": ordered_locations,
        "ordered_coordinates": ordered_coordinates,
    }


@router.get("/loc_coord/{chat_id}")
async def get_coord_from_chat(
    chat_id: str, x_session_id: str = Header(None, alias="X-Session-ID")
):
    # Construct the file path
    file_path = f"chat-history/llm-sf/{x_session_id}/{chat_id}.json"

    # Check if the file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Chat file not found")

    # Read and parse the JSON file
    try:
        with open(file_path, "r") as file:
            iti_first_draft = json.load(file)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")

    # Extract the required fields with error handling
    try:
        print("x_session_id:", x_session_id)
        print("chat_id:", iti_first_draft["chat_id"])
        print("title:", iti_first_draft["title"])

        ordered_locations = iti_first_draft["messages"][2]
        ordered_coordinates = iti_first_draft["messages"][3]
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing key in JSON: {str(e)}")
    except IndexError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Index out of range when accessing 'messages': {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing JSON data: {str(e)}"
        )

    return {
        "ordered_locations": ordered_locations,
        "ordered_coordinates": ordered_coordinates,
    }
