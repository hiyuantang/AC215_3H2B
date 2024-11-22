import os
import re
from fastapi import HTTPException
import traceback
from vertexai.generative_models import GenerativeModel
from api.utils.input_base import UserInput

# Setup
GCP_PROJECT = os.environ["GCP_PROJECT"]
GCP_LOCATION = "us-central1"
MODEL_ENDPOINT = (
    "projects/184619367894/locations/us-central1/endpoints/228541188414636032"
)

# Configuration settings for the content generation
generation_config = {
    "max_output_tokens": 3000,  # Maximum number of tokens for output
    "temperature": 0.75,  # Control randomness in output
    "top_p": 0.95,  # Use nucleus sampling
}

generative_model = GenerativeModel(MODEL_ENDPOINT)


def generate_chat_response(input_data: UserInput) -> str:
    """
    Generate a response using the chat session to maintain history.
    Handles both text and image inputs.

    Args:
        chat_session: The Vertex AI chat session
        message: Dict containing 'content' (text) and optionally 'image' (base64 string)

    Returns:
        str: The model's response
    """
    city = input_data.city
    days = input_data.days
    type = input_data.type
    month = input_data.month

    query = f"Location: {city}, Days: {days}, Month: {month}, Type: {type}. This is the first stage of creating an itinerary. As a professional travel planner, can you create a concise itinerary using the TDLN format? TDLN includes only the theme, days, and location names, each on a new line. The format requires that no '()' be used to explain the location, and no additional information should be provided unless specified in the prompt."

    try:
        # Send message with all parts to the model
        response = generative_model.generate_content(
            [query],  # Input prompt
            generation_config=generation_config,  # Configuration settings
            stream=False,  # Enable streaming for responses
        )

        return response.text

    except Exception as e:
        print(f"Error generating response: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to generate response: {str(e)}"
        )


def prepare_response(response_text):
    # Split the text into lines
    lines = response_text.strip().split("\n")

    # The first line is assumed to be the title
    title = lines[0].strip()

    # Initialize empty dictionaries to hold the itinerary and themes
    itinerary = {}
    themes = {}

    current_day = None

    # Compile a regex pattern to match 'Day x' where x is a number
    day_pattern = re.compile(r"Day\s*(\d+):?", re.IGNORECASE)

    for line in lines[1:]:
        line = line.strip()

        # Check if the line indicates a new day
        day_match = day_pattern.match(line)
        if day_match:
            # Extract the day number
            current_day = int(day_match.group(1))
            # Initialize the list for this day's locations
            itinerary[current_day] = []
            # Extract any theme on the same line after 'Day x:'
            day_line = line[day_match.end() :].strip(":- ")
            if day_line:
                themes[current_day] = day_line
            else:
                themes[current_day] = None
        elif line:
            # This line contains a location or activity
            if current_day is None:
                continue  # Skip lines before the first 'Day x'
            # Remove leading dashes or bullets and strip whitespace
            location = line.lstrip("-•").strip()
            # Ignore empty lines
            if location:
                itinerary[current_day].append(location)
    return title, itinerary, themes
