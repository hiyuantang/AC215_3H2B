import os
from typing import Dict
from fastapi import HTTPException
import traceback
import chromadb
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from vertexai.generative_models import GenerativeModel, ChatSession


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
Your responses are based solely on the information provided in the text 
chunks given to you. Do not use any external knowledge or make assumptions 
beyond what is explicitly stated in these chunks.

When answering a query:
1. Carefully read all the text chunks provided.
2. Identify the most relevant information from these chunks to address the user's question.
3. Formulate your response using only the information found in the given chunks.
4. If the provided chunks do not contain sufficient information to answer the query, state that you don't have enough information to provide a complete answer.
5. Always maintain a professional and knowledgeable tone, befitting a travel and tourism agent.
6. If there are contradictions in the provided chunks, mention this in your response and explain the different viewpoints presented.

Remember:
- You are an expert in tourist locations, but your knowledge is limited to the information in the provided chunks.
- Do not invent information or draw from knowledge outside of the given text chunks.
- If asked about topics unrelated to traveling or tourist locations, politely redirect the conversation back to traveling-related subjects.
- Be concise in your responses while ensuring you cover all relevant information from the chunks.

Your goal is to provide accurate, helpful information about traveling and tourist locations 
based heavily on the content of the text chunks you receive with each query.
"""
generative_model = GenerativeModel(
	GENERATIVE_MODEL,
	system_instruction=[SYSTEM_INSTRUCTION]
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
	query_embedding_inputs = [TextEmbeddingInput(task_type='RETRIEVAL_DOCUMENT', text=query)]
	kwargs = dict(output_dimensionality=EMBEDDING_DIMENSION) if EMBEDDING_DIMENSION else {}
	embeddings = embedding_model.get_embeddings(query_embedding_inputs, **kwargs)
	return embeddings[0].values

def generate_chat_response(title: str, ordered_locations: Dict, ordered_coordinates: Dict) -> str:
     title_enhance = title * 5
     
     query = '''I have this travel itinerary: 1-Day Solo Itinerary in Beijing for April\nDay 1: Journey 
            Through Imperial Majesty\n- Forbidden City\n- Temple of Heaven\n- Summer Palace. 
            Expand on how and why those locations are a good solo trip. 
            At the start of the itinerary, give an interesting introduction to the destination regarding city's
            hitory, culture, etc. For the main body of the answer, give me a more detailed traval itinerary without 
            changing my plan, meaning no change of days and the locations in the original plan. At the end of the 
            itinerary, give user tips specifically for this travel, considering about the month and its respective 
            season.'''
     

    try:
        # Initialize parts list for the message
        message_parts = []

        # Add text content if present
        if message.get("content"):
            # Create embeddings for the message content
            query_embedding = _generate_query_embedding(message["content"])
            # Retrieve chunks based on embedding value 
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=5
            )
            INPUT_PROMPT = f"""
            {message["content"]}
            {results["documents"][0]}
            """
            message_parts.append(INPUT_PROMPT)
                    
        
        if not message_parts:
            raise ValueError("Message must contain text content")

        # Send message with all parts to the model
        response = generative_model.generate_content(
            [message_parts],  # Input prompt
            generation_config=generation_config,  # Configuration settings
            stream=False,  # Enable streaming for responses
        )
        
        return response.text
        
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate response: {str(e)}"
        )