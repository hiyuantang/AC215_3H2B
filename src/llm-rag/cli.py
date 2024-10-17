import os
import argparse
import pandas as pd
import json
import time
import glob
import hashlib
import chromadb

# Vertex AI
import vertexai
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from vertexai.generative_models import GenerativeModel, GenerationConfig, Content, Part, ToolConfig

# Langchain
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
#from langchain_experimental.text_splitter import SemanticChunker
from semantic_splitter import SemanticChunker
import agent_tools

# Setup
GCP_PROJECT = os.environ["GCP_PROJECT"]
GCP_LOCATION = os.environ["GCP_LOCATION"]
EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIMENSION = 256
GENERATIVE_MODEL = "gemini-1.5-flash-002"
INPUT_FOLDER = "input-datasets"
OUTPUT_FOLDER = "outputs"
CHROMADB_HOST = "llm-rag-chromadb"
CHROMADB_PORT = 8000
vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)
# https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/text-embeddings-api#python
embedding_model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)
# Configuration settings for the content generation
generation_config = {
    "max_output_tokens": 8192,  # Maximum number of tokens for output
    "temperature": 0.25,  # Control randomness in output
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
based solely on the content of the text chunks you receive with each query.
"""
generative_model = GenerativeModel(
	GENERATIVE_MODEL,
	system_instruction=[SYSTEM_INSTRUCTION]
)

city_mappings = {
    "Amsterdam": {"country": "Netherlands", "continent": "Europe"},
    "Athens": {"country": "Greece", "continent": "Europe"},
    "Bangkok": {"country": "Thailand", "continent": "Asia"},
    "Barcelona": {"country": "Spain", "continent": "Europe"},
    "Beijing": {"country": "China", "continent": "Asia"},
    "Berlin": {"country": "Germany", "continent": "Europe"},
    "Bogota": {"country": "Colombia", "continent": "South America"},
    "Buenos Aires": {"country": "Argentina", "continent": "South America"},
    "Cairo": {"country": "Egypt", "continent": "Africa"},
    "Cape Town": {"country": "South Africa", "continent": "Africa"},
    "Caracas": {"country": "Venezuela", "continent": "South America"},
    "Castleton": {"country": "United Kingdom", "continent": "Europe"},
    "Copenhagen": {"country": "Denmark", "continent": "Europe"},
    "Dubai": {"country": "United Arab Emirates", "continent": "Asia"},
    "Dublin": {"country": "Ireland", "continent": "Europe"},
    "Helsinki": {"country": "Finland", "continent": "Europe"},
    "Hong Kong": {"country": "China", "continent": "Asia"},
    "Istanbul": {"country": "Turkey", "continent": "Europe"},
    "Jakarta": {"country": "Indonesia", "continent": "Asia"},
    "Kabwe": {"country": "Zambia", "continent": "Africa"},
    "Kuala Lumpur": {"country": "Malaysia", "continent": "Asia"},
    "Lima": {"country": "Peru", "continent": "South America"},
    "Lisbon": {"country": "Portugal", "continent": "Europe"},
    "London": {"country": "United Kingdom", "continent": "Europe"},
    "Los Angeles": {"country": "United States", "continent": "North America"},
    "Melbourne": {"country": "Australia", "continent": "Australia"},
    "Mexico City": {"country": "Mexico", "continent": "North America"},
    "Milan": {"country": "Italy", "continent": "Europe"},
    "Montreal": {"country": "Canada", "continent": "North America"},
    "Moscow": {"country": "Russia", "continent": "Europe"},
    "Mumbai": {"country": "India", "continent": "Asia"},
    "New Delhi": {"country": "India", "continent": "Asia"},
    "New York City": {"country": "United States", "continent": "North America"},
    "Oslo": {"country": "Norway", "continent": "Europe"},
    "Paris": {"country": "France", "continent": "Europe"},
    "Prague": {"country": "Czech Republic", "continent": "Europe"},
    "Rio de Janeiro": {"country": "Brazil", "continent": "South America"},
    "Rome": {"country": "Italy", "continent": "Europe"},
    "Saint Petersburg": {"country": "Russia", "continent": "Europe"},
    "San Francisco": {"country": "United States", "continent": "North America"},
    "São Paulo": {"country": "Brazil", "continent": "South America"},
    "Seoul": {"country": "South Korea", "continent": "Asia"},
    "Shanghai": {"country": "China", "continent": "Asia"},
    "Singapore": {"country": "Singapore", "continent": "Asia"},
    "Stockholm": {"country": "Sweden", "continent": "Europe"},
    "Sydney": {"country": "Australia", "continent": "Australia"},
    "Taipei": {"country": "Taiwan", "continent": "Asia"},
    "Tel Aviv": {"country": "Israel", "continent": "Asia"},
    "Tokyo": {"country": "Japan", "continent": "Asia"},
    "Vienna": {"country": "Austria", "continent": "Europe"},
    "Warsaw": {"country": "Poland", "continent": "Europe"},
}


def generate_query_embedding(query):
	query_embedding_inputs = [TextEmbeddingInput(task_type='RETRIEVAL_DOCUMENT', text=query)]
	kwargs = dict(output_dimensionality=EMBEDDING_DIMENSION) if EMBEDDING_DIMENSION else {}
	embeddings = embedding_model.get_embeddings(query_embedding_inputs, **kwargs)
	return embeddings[0].values


def generate_text_embeddings(chunks, dimensionality: int = 256, batch_size=250):
	# Max batch size is 250 for Vertex AI
	all_embeddings = []
	for i in range(0, len(chunks), batch_size):
		batch = chunks[i:i+batch_size]
		inputs = [TextEmbeddingInput(text, "RETRIEVAL_DOCUMENT") for text in batch]
		kwargs = dict(output_dimensionality=dimensionality) if dimensionality else {}
		embeddings = embedding_model.get_embeddings(inputs, **kwargs)
		all_embeddings.extend([embedding.values for embedding in embeddings])

	return all_embeddings


def load_text_embeddings(df, collection, batch_size=500):

	# Generate ids
	df["id"] = df.index.astype(str)
	hashed_cities = df["city"].apply(lambda x: hashlib.sha256(x.encode()).hexdigest()[:16])
	df["id"] = hashed_cities + "-" + df["id"]

	metadata = {
		"city": df["city"].tolist()[0]
	}
	if metadata["city"] in city_mappings:
		city_mapping = city_mappings[metadata["city"]]
		metadata["country"] = city_mapping["country"]
		metadata["continent"] = city_mapping["continent"]
   
	# Process data in batches
	total_inserted = 0
	for i in range(0, df.shape[0], batch_size):
		# Create a copy of the batch and reset the index
		batch = df.iloc[i:i+batch_size].copy().reset_index(drop=True)

		ids = batch["id"].tolist()
		documents = batch["chunk"].tolist() 
		metadatas = [metadata for item in batch["city"].tolist()]
		embeddings = batch["embedding"].tolist()

		collection.add(
			ids=ids,
			documents=documents,
			metadatas=metadatas,
			embeddings=embeddings
		)
		total_inserted += len(batch)
		print(f"Inserted {total_inserted} items...")

	print(f"Finished inserting {total_inserted} items into collection '{collection.name}'")


def chunk(method="char-split"):
	print("chunk()")

	# Make dataset folders
	os.makedirs(OUTPUT_FOLDER, exist_ok=True)

	# Get the list of text file
	text_files = glob.glob(os.path.join(INPUT_FOLDER, "cities-wiki", "*.txt"))
	print("Number of files to process:", len(text_files))

	# Process
	for text_file in text_files:
		print("Processing file:", text_file)
		filename = os.path.basename(text_file)
		city_name = filename.split(".")[0]

		with open(text_file) as f:
			input_text = f.read()
		
		text_chunks = None
		if method == "char-split":
			chunk_size = 350
			chunk_overlap = 20
			# Init the splitter
			text_splitter = CharacterTextSplitter(chunk_size = chunk_size, chunk_overlap=chunk_overlap, separator='', strip_whitespace=False)

			# Perform the splitting
			text_chunks = text_splitter.create_documents([input_text])
			text_chunks = [doc.page_content for doc in text_chunks]
			print("Number of chunks:", len(text_chunks))

		elif method == "recursive-split":
			chunk_size = 350
			# Init the splitter
			text_splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size)

			# Perform the splitting
			text_chunks = text_splitter.create_documents([input_text])
			text_chunks = [doc.page_content for doc in text_chunks]
			print("Number of chunks:", len(text_chunks))
		
		elif method == "semantic-split":
			# Init the splitter
			text_splitter = SemanticChunker(embedding_function=generate_text_embeddings)
			# Perform the splitting
			text_chunks = text_splitter.create_documents([input_text])
			
			text_chunks = [doc.page_content for doc in text_chunks]
			print("Number of chunks:", len(text_chunks))

		if text_chunks is not None:
			# Save the chunks
			data_df = pd.DataFrame(text_chunks,columns=["chunk"])
			data_df["city"] = city_name
			print("Shape:", data_df.shape)
			print(data_df.head())

			jsonl_filename = os.path.join(OUTPUT_FOLDER, f"chunks-{method}-{city_name}.jsonl")
			with open(jsonl_filename, "w") as json_file:
				json_file.write(data_df.to_json(orient='records', lines=True))


def embed(method="char-split"):
	print("embed()")

	# Get the list of chunk files
	jsonl_files = glob.glob(os.path.join(OUTPUT_FOLDER, f"chunks-{method}-*.jsonl"))
	print("Number of files to process:", len(jsonl_files))

	# Process
	for jsonl_file in jsonl_files:
		print("Processing file:", jsonl_file)

		data_df = pd.read_json(jsonl_file, lines=True)
		print("Shape:", data_df.shape)
		print(data_df.head())

		chunks = data_df["chunk"].values
		if method == "semantic-split":
			embeddings = generate_text_embeddings(chunks,EMBEDDING_DIMENSION, batch_size=15)
		else:
			embeddings = generate_text_embeddings(chunks,EMBEDDING_DIMENSION, batch_size=100)
		data_df["embedding"] = embeddings

		# Save 
		print("Shape:", data_df.shape)
		print(data_df.head())

		jsonl_filename = jsonl_file.replace("chunks-","embeddings-")
		with open(jsonl_filename, "w") as json_file:
			json_file.write(data_df.to_json(orient='records', lines=True))


def load(method="char-split"):
	print("load()")

	# Connect to chroma DB
	client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)

	# Get a collection object from an existing collection, by name. If it doesn't exist, create it.
	collection_name = f"{method}-collection"
	print("Creating collection:", collection_name)

	try:
		# Clear out any existing items in the collection
		client.delete_collection(name=collection_name)
		print(f"Deleted existing collection '{collection_name}'")
	except Exception:
		print(f"Collection '{collection_name}' did not exist. Creating new.")

	collection = client.create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})
	print(f"Created new empty collection '{collection_name}'")
	print("Collection:", collection)

	# Get the list of embedding files
	jsonl_files = glob.glob(os.path.join(OUTPUT_FOLDER, f"embeddings-{method}-*.jsonl"))
	print("Number of files to process:", len(jsonl_files))

	# Process
	for jsonl_file in jsonl_files:
		print("Processing file:", jsonl_file)

		data_df = pd.read_json(jsonl_file, lines=True)
		print("Shape:", data_df.shape)
		print(data_df.head())

		# Load data
		load_text_embeddings(data_df, collection)


def query(method="char-split"):
	print("load()")

	# Connect to chroma DB
	client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)

	# Get a collection object from an existing collection, by name. If it doesn't exist, create it.
	collection_name = f"{method}-collection"

	query = '''I have this travel itinerary: 1-Day Solo Itinerary in Beijing for April\nDay 1: Journey 
	Through Imperial Majesty\n- Forbidden City\n- Temple of Heaven\n- Summer Palace. 
	Expand on how and why those locations are a good solo trip. 
	At the start of the itinerary, give an interesting introduction to the destination regarding city's
	hitory, culture, etc. For the main body of the answer, give me a more detailed traval itinerary without 
	changing my plan, meaning no change of days and the locations in the original plan. At the end of the 
	itinerary, give user tips specifically for this travel, considering about the month and its respective 
	season. '''
	
	query_embedding = generate_query_embedding(query)
	print("Embedding values:", query_embedding)

	# Get the collection
	collection = client.get_collection(name=collection_name)

	# 1: Query based on embedding value 
	results = collection.query(
		query_embeddings=[query_embedding],
		n_results=10
	)
	print("Query:", query)
	print("\n\nResults:", results)

	# 2: Query based on embedding value + metadata filter
	results = collection.query(
		query_embeddings=[query_embedding],
		n_results=10,
		where={"city":"London"}
	)
	print("Query:", query)
	print("\n\nResults:", results)

	# 3: Query based on embedding value + lexical search filter
	search_string = "Italian"
	results = collection.query(
		query_embeddings=[query_embedding],
		n_results=10,
		where_document={"$contains": search_string}
	)
	print("Query:", query)
	print("\n\nResults:", results)


def chat(method="char-split"):
	print("chat()")

	# Connect to chroma DB
	client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
	# Get a collection object from an existing collection, by name. If it doesn't exist, create it.
	collection_name = f"{method}-collection"

	query = '''I have this travel itinerary: 1-Day Solo Itinerary in Beijing for April\nDay 1: Journey Through Imperial Majesty\n- Forbidden City\n- Temple of Heaven\n- Summer Palace. 
	Expand on how and why those locations are a good solo trip. 
	At the start of the itinerary, give an interesting introduction to Beijing regarding Beijing's
	hitory, culture, etc. For the main body of the answer, give me a more detailed traval itinerary without 
	changing my plan, meaning no change of days and the locations in the original plan. At the end of the 
	itinerary, give user tips specifically for this travel, considering about the month and its respective 
	season. '''
	query_embedding = generate_query_embedding(query)
	print("Query:", query)
	print("Embedding values:", query_embedding)
	# Get the collection
	collection = client.get_collection(name=collection_name)

	# Query based on embedding value 
	results = collection.query(
		query_embeddings=[query_embedding],
		n_results=10
	)
	print("\n\nResults:", results)

	print(len(results["documents"][0]))

	INPUT_PROMPT = f"""
	{query}
	{"\n".join(results["documents"][0])}
	"""

	print("INPUT_PROMPT: ",INPUT_PROMPT)
	response = generative_model.generate_content(
		[INPUT_PROMPT],  # Input prompt
		generation_config=generation_config,  # Configuration settings
		stream=False,  # Enable streaming for responses
	)
	generated_text = response.text
	print("LLM Response:", generated_text)


def get(method="char-split"):
	print("get()")

	# Connect to chroma DB
	client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
	# Get a collection object from an existing collection, by name. If it doesn't exist, create it.
	collection_name = f"{method}-collection"

	# Get the collection
	collection = client.get_collection(name=collection_name)

	# Get documents with filters
	results = collection.get(
		where={"city":"London"},
		limit=10
	)
	print("\n\nResults:", results)


def agent(method="char-split"):
	print("agent()")

	# Connect to chroma DB
	client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
	# Get a collection object from an existing collection, by name. If it doesn't exist, create it.
	collection_name = f"{method}-collection"
	# Get the collection
	collection = client.get_collection(name=collection_name)

	# User prompt
	user_prompt_content = Content(
    	role="user",
		parts=[
			Part.from_text("Describe the history of London"),
		],
	)
	
	# Step 1: Prompt LLM to find the tool(s) to execute to find the relevant chunks in vector db
	print("user_prompt_content: ",user_prompt_content)
	response = generative_model.generate_content(
		user_prompt_content,
		generation_config=GenerationConfig(temperature=0),  # Configuration settings
		tools=[agent_tools.travel_expert_tool],  # Tools available to the model
		tool_config=ToolConfig(
			function_calling_config=ToolConfig.FunctionCallingConfig(
				# ANY mode forces the model to predict only function calls
				mode=ToolConfig.FunctionCallingConfig.Mode.ANY,
		))
	)
	print("LLM Response:", response)

	# Step 2: Execute the function and send chunks back to LLM to answer get the final response
	function_calls = response.candidates[0].function_calls
	print("Function calls:")
	function_responses = agent_tools.execute_function_calls(function_calls,collection,embed_func=generate_query_embedding)
	if len(function_responses) == 0:
		print("Function calls did not result in any responses...")
	else:
		# Call LLM with retrieved responses
		response = generative_model.generate_content(
			[
				user_prompt_content,  # User prompt
				response.candidates[0].content,  # Function call response
				Content(
					parts=function_responses
				),
			],
			tools=[agent_tools.travel_expert_tool],
		)
		print("LLM Response:", response)


def main(args=None):
	print("CLI Arguments:", args)

	if args.chunk:
		chunk(method=args.chunk_type)

	if args.embed:
		embed(method=args.chunk_type)

	if args.load:
		load(method=args.chunk_type)

	if args.query:
		query(method=args.chunk_type)
	
	if args.chat:
		chat(method=args.chunk_type)
	
	if args.get:
		get(method=args.chunk_type)
	
	if args.agent:
		agent(method=args.chunk_type)


if __name__ == "__main__":
	# Generate the inputs arguments parser
	# if you type into the terminal '--help', it will provide the description
	parser = argparse.ArgumentParser(description="CLI")

	parser.add_argument(
		"--chunk",
		action="store_true",
		help="Chunk text",
	)
	parser.add_argument(
		"--embed",
		action="store_true",
		help="Generate embeddings",
	)
	parser.add_argument(
		"--load",
		action="store_true",
		help="Load embeddings to vector db",
	)
	parser.add_argument(
		"--query",
		action="store_true",
		help="Query vector db",
	)
	parser.add_argument(
		"--chat",
		action="store_true",
		help="Chat with LLM",
	)
	parser.add_argument(
		"--get",
		action="store_true",
		help="Get documents from vector db",
	)
	parser.add_argument(
		"--agent",
		action="store_true",
		help="Chat with LLM Agent",
	)
	parser.add_argument("--chunk_type", default="char-split", help="char-split | recursive-split | semantic-split")

	args = parser.parse_args()

	main(args)