import os
from typing import Dict
from fastapi import HTTPException
import traceback
import chromadb
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from vertexai.generative_models import GenerativeModel


# Setup
GCP_PROJECT = os.environ["GCP_PROJECT"]
GCP_LOCATION = "us-central1"
EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIMENSION = 256
GENERATIVE_MODEL = "gemini-1.5-flash-002"
CHROMADB_HOST = os.environ["CHROMADB_HOST"]
CHROMADB_PORT = os.environ["CHROMADB_PORT"]

# Configuration settings for the content generation
generation_config = {
    "max_output_tokens": 3000,  # Maximum number of tokens for output
    "temperature": 0.1,  # Control randomness in output
    "top_p": 0.95,  # Use nucleus sampling
}

# Initialize the GenerativeModel with specific system instructions
SYSTEM_INSTRUCTION = """
You are an AI assistant specialized in locations and attractions for tourism.

When answering a query:
1. Carefully read all the text chunks provided.
2. Identify the most relevant information from these chunks to address the user's question.
3. Formulate your response enhanced by the information found in the given chunks.
4. If the provided chunks do not contain sufficient information to answer the query, use your own knowledge.
5. Always maintain a professional and knowledgeable tone, befitting a travel and tourism agent.

Remember:
- You are an expert in tourist locations, and your knowledge is enhanced by the information in the provided chunks.
- If asked about topics unrelated to traveling or tourist locations, politely redirect the conversation back to traveling-related subjects.

Your goal is to provide accurate, helpful information about traveling and tourist locations
helped by the content of the text chunks you receive with each query.
"""
generative_model = GenerativeModel(
    GENERATIVE_MODEL, system_instruction=[SYSTEM_INSTRUCTION]
)
# https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/text-embeddings-api#python
embedding_model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)

# Connect to chroma DB
client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
method = "recursive-split"
collection_name = f"{method}-collection"
# Get the collection
collection = client.get_collection(name=collection_name)


def _generate_query_embedding(query):
    """
    Generates an embedding for the given query using the specified embedding model.

    Args:
        query (str): The input text for which the embedding is to be generated.

    Returns:
        list: A list of embedding values for the input query.
    """
    query_embedding_inputs = [
        TextEmbeddingInput(task_type="RETRIEVAL_DOCUMENT", text=query)
    ]
    kwargs = (
        dict(output_dimensionality=EMBEDDING_DIMENSION) if EMBEDDING_DIMENSION else {}
    )
    embeddings = embedding_model.get_embeddings(query_embedding_inputs, **kwargs)
    return embeddings[0].values


def generate_chat_response(
    title: str, ordered_locations: Dict, days_themes: Dict
) -> str:
    """
    Generates a detailed travel itinerary based on the provided title, ordered locations, and themes for each day.
    Args:
        title (str): The title of the travel itinerary.
        ordered_locations (Dict): A dictionary where keys are days and values are lists of locations in order.
        days_themes (Dict): A dictionary where keys are days and values are themes for each day.
    Returns:
        str: A detailed travel itinerary as a string.
    Raises:
        HTTPException: If there is an error generating the response.
    """
    # Query construction
    query_list = []
    for day, theme in days_themes.items():
        locations = ", ".join(ordered_locations[day])
        query_list.append(f"Day {day}: {theme} (locations: {locations})")

        query = ". ".join(query_list)
    query = f"Travel Itinerary: {title}. " + query
    print(query)

    rag_query = query * 3

    query = (
        query
        + """. Please create a more comprehensive itinerary based on the outline provided. Do not change the days,
    themes, or locations listed. Maintain the same order of activities and locations. Your task is to enhance the itinerary with
    detailed and descriptive information about each day while keeping the structure intact.
    At the start of the itinerary, include an engaging introduction to the destination city, highlighting the city’s
    history, culture, and charm.
    In the main body, provide a detailed travel itinerary for each day according to the themes and locations specified in
    the original plan. Avoid altering the days, themes, or location sequence. Do not arrange time, such as morning, afternoon, evening.
    Each location should be separated as a bullet point.
    At the end of the itinerary, offer travel tips tailored to the season, specifically for February,
    ensuring visitors can make the most of their trip."""
    )

    try:
        # Create embeddings for the message content
        query_embedding = _generate_query_embedding(rag_query)
        # Retrieve chunks based on embedding value
        results = collection.query(query_embeddings=[query_embedding], n_results=5)
        INPUT_PROMPT = f"""
        {query}
        {"Additional information (Use information below to enhance itinerary descriptions for introduction, locations, and tips): "}
        {results["documents"][0]}
        """

        # Send message with all parts to the model
        response = generative_model.generate_content(
            [INPUT_PROMPT],  # Input prompt
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
