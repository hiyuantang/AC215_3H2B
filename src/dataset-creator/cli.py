import os
import argparse
import pandas as pd
import json
import time
import glob
from sklearn.model_selection import train_test_split
from google.cloud import storage
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting, FinishReason
import vertexai.generative_models as generative_models

# Setup
GCP_PROJECT = os.environ["GCP_PROJECT"]
GCP_LOCATION = os.environ["GCP_LOCATION"]
GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]
GENERATIVE_MODEL = "gemini-1.5-flash-001"
OUTPUT_FOLDER = "data"
# Configuration settings for the content generation
generation_config = {
    "max_output_tokens": 8192,  # Maximum number of tokens for output
    "temperature": 1,  # Control randomness in output
    "top_p": 0.95,  # Use nucleus sampling
}

# Safety settings to filter out harmful content
safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH
    )
]

# System Prompt
SYSTEM_INSTRUCTION = """Generate a set of 20 question-answer pairs about travel itinerary in English. Adhere to the following guidelines:

1. Question Independence:
    - Ensure each question-answer pair is completely independent and self-contained
    - Do not reference other questions or answers within the set
    - Each Q&A pair should be understandable without any additional context
    - Each question should follow strict format, include information about city, days, month, and travel type
    - Each question days item should between 1 to 10
    - Each question month item should between January to December
    - Each question travel type item could be as creative as possible

2. Question Types:
    - Include a variety of question types (e.g., "what", "how", "can you", "how can I", "what about") about creating or crafting the travel itinerary given the information of city, days, month, and travel type
    - Must ask to craft the travel itinerary that is extremely concise. 
    - Each question's asking for a concise itinerary should match the format of answer, for example: "Can you craft a concise thematic itinerary with only days and locations? Do not mind hotels or where I live in that city."
    - Formulate questions as if someone is passionate about travel
    - Ensure questions cover a wide range of travel type including both positive and negative words (e.g., Introspective, Healing, Nostalgic, Spiritual, Adventure, Cultural, Solo, Family Bonding, Luxury, Ecotourism, Culinary, Educational, Retreat, Romantic, Boring, Losing Love, Losing Friends, Losing Family Members, Historic, Wellness)

3. Think before answering:
    - Input Information: Start by considering the city name, duration of stay, type of trip, and the month of travel. These elements will guide the themes and activities.
    - Assuming the type of trip is what traveller want to have, regardless of positive or negative. For example, if type is Boring, it means that the traveller needs a travel itinerary that makes them feel boring. 
    - Daily Themes: For each day, develop a distinct theme based on the trip type and month. For example, in Paris for a romantic trip in April, themes might include "Art and Romance," "Secluded Gardens," and "Gourmet Experience." Avoid using trivial words (e.g, iconic)
    - Seasonal Influence: Reflect on how the season affects the city. Consider weather conditions, local festivals, and seasonal attractions. For instance, visiting Tokyo in March would include cherry blossom viewing, which is both seasonal and thematic.
    - Location Selection: Based on daily themes and seasonal influence, carefully choose the best locations accordingly for each day. 
    - Experiential Rewards: Consider what travelers gain from visiting these locations. This could be cultural enrichment, relaxation, adventure, or bonding experiences. For example, exploring Kyoto temples in fall provides a serene and visually stunning experience due to the autumn foliage.
    - Logistical Considerations: Ensure the itinerary is location rich and allows for rest and spontaneity.
    - Final Reflection: Reflection on how the planned itinerary allows travelers to immerse themselves fully in the city culture, beauty, and uniqueness. Highlight the personal growth or memories they might take away from this experience.

4. Answer Format:
    - Begin each answer from summarizing the prompt information about travel city, duration, month, and type. For example:
        * "3-Day Family Itinerary in Paris for December"
        * "1-Day Solo travel plan in Beijing for April"
        * "Boring April Itinerary in Vienna for 5 days"

5. Final answer content:
    - The answer must strictly follow the specified format and contain only day, theme, and location information without any excessive output.
    - The answer must include only day, theme, and location names.
    - The answer must be extremely concise and clear, adhering to the output format.
    - The answer should include creative theme name. 
    - The answer must be definitive; do not offer options or alternative plans.
    - The answer must use specific location names; do not only use general terms like "cafe" or "restaurant."
    - The answer should not suggest living places like hotel, unless its recommending hotel's rooftop bar. 
    - The answer should not explain the rationale or description of the locations.
    - The answer should not include morning, afternoon, or evening.
    - The answer should not include any closing remarks. 
    - The answer must not use parentheses, or '()' to comment any location. 

6. Language:
    - Use English throughout

Output Format:
Provide the Q&A pairs in JSON format, with each pair as an object containing 'question' and 'answer' fields, within a JSON array.
Follow these strict guidelines:
1. Use double quotes for JSON keys and string values.
2. For any quotation marks within the text content, use single quotes (') instead of double quotes. Avoid quotation marks.
3. If a single quote (apostrophe) appears in the text, escape it with a backslash (\'). 
4. Ensure there are no unescaped special characters that could break the JSON structure.
5. Avoid any Invalid control characters that JSON decode will not be able to decode.

Here's an example of the expected format:
Sample JSON Output:
```json
[
  {
    "question": "Location: Paris, Days: 3, month: December, type: family. Given the information, can you craft a concise itinerary with only location and days information and structure it cleanly?",
    "answer": "3-Day Family Itinerary in Paris for December\nDay 1: Parisian Landmarks and Lights\n- Eiffel Tower\n- Seine River Cruise\n- Cathédrale Notre-Dame de Paris\n- Champs-Élysées Christmas Market\nDay 2: Artistic Odyssey Through Time\n- Louvre Museum\n- Musée d'Orsay\n- Montmartre\n- Sacré-Cœur Basilica\nDay 3: Enchanted Escapes and Hidden Gems\n- Palace of Versailles\n- Le Marais District\n- Centre Pompidou"
  },
  {
    "question": "I would like to go to Beijing for 1 day alone. Could you craft a travel itinerary that is clean and concise with only necessary information on days and locations?",
    "answer": "1-Day Solo Itinerary in Beijing for April\nDay 1: Journey Through Imperial Majesty\n- Forbidden City\n- Temple of Heaven\n- Summer Palace"
  },
  {
    "question": "I want to travel to Barcelona for 3 days in June for a Healing journey. Could you craft a clean and concise itinerary with only days and locations? Do not mind hotels or where I live in that city.",
    "answer": "3-Day Healing Itinerary in Barcelona for June\nDay 1: Coastal Tranquility and Mindful Movement\n- Barceloneta Beach\n- Park Güell\n- Sagrada Família\nDay 2: Natural Serenity and Artistic Inspiration\n- Tibidabo Mountain\n- Parc de la Ciutadella\n- Picasso Museum\nDay 3: Historical Reflections and Inner Peace\n- Gothic Quarter\n- Barcelona Cathedral\n- Monastery of Pedralbes"
  }
]
```

Note: The sample JSON provided includes only three Q&A pairs for brevity. The actual output should contain all 20 pairs as requested."""

INPUT_PROMPT = """Generate 20 diverse, informative, and engaging question-answer pairs about extremely concise travel itinary following these guidelines. Ensure each pair is independent and self-contained. """
NUM_ITERATIONS = 1 # Loop to generate and save the content

def generate():
    print("generate()")

    # Make dataset folders
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Initialize Vertex AI project and location
    vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)
    
    # Initialize the GenerativeModel with specific system instructions
    model = GenerativeModel(
        GENERATIVE_MODEL,
        system_instruction=[SYSTEM_INSTRUCTION]
    )

    for i in range(0, NUM_ITERATIONS):
        print(f"Generating batch: {i}")
        try:
          responses = model.generate_content(
            [INPUT_PROMPT],  # Input prompt
            generation_config=generation_config,  # Configuration settings
            safety_settings=safety_settings,  # Safety settings
            stream=False,  # Enable streaming for responses
          )
          generated_text = responses.text

          # Create a unique filename for each iteration
          file_name = f"{OUTPUT_FOLDER}/strict_format_qa_{i}.txt"
          # Save
          with open(file_name, "w") as file:
            file.write(generated_text)
        except Exception as e:
          print(f"Error occurred while generating content: {e}")

def save_prompt():
    # Create a DataFrame
    data = {
        'SYSTEM_INSTRUCTION': [SYSTEM_INSTRUCTION],
        'INPUT_PROMPT': [INPUT_PROMPT],
        'NUM_ITERATIONS': [NUM_ITERATIONS]
    }
    df = pd.DataFrame(data)

    # Define the filename
    filename = os.path.join(OUTPUT_FOLDER, "sys-instruct.csv")

    # Write the DataFrame to a CSV file
    df.to_csv(filename, index=False)

    # # Read the DataFrame
    # df_read = pd.read_csv(filename)
    # for index, row in df_read.iterrows():
    #     print("System Instruction:", row['SYSTEM_INSTRUCTION'])
    #     print("Input Prompt:", row['INPUT_PROMPT'])
    #     print("Number of Iterations:", row['NUM_ITERATIONS'])
    #     print("\n" + "-"*40 + "\n")

def prepare():
    print("prepare()")

    # Get the generated files
    output_files = glob.glob(os.path.join(OUTPUT_FOLDER, "strict_format_qa_*.txt"))
    output_files.sort()

    # Consolidate the data
    output_pairs = []
    errors = []
    for output_file in output_files:
        print("Processing file:", output_file)
        with open(output_file, "r") as read_file:
            text_response = read_file.read()
        
        text_response = text_response.replace("```json","").replace("```","")

        try:
            json_responses = json.loads(text_response)
            output_pairs.extend(json_responses)
        
        except Exception as e:
            errors.append({"file": output_file, "error": str(e)})
    
    print("Number of errors:", len(errors))
    print(errors[:5])

    # Save the dataset
    output_pairs_df = pd.DataFrame(output_pairs)
    output_pairs_df.drop_duplicates(subset=['question'], inplace=True)
    output_pairs_df = output_pairs_df.dropna()
    print("Shape:", output_pairs_df.shape)
    print(output_pairs_df.head())
    filename = os.path.join(OUTPUT_FOLDER, "instruct-dataset.csv")
    output_pairs_df.to_csv(filename, index=False)

    # Build training formats
    output_pairs_df['text'] = "human: " + output_pairs_df['question'] + "\n" + "bot: " + output_pairs_df['answer']
    
    # Gemini Data prep: https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini-supervised-tuning-prepare
    # {"contents":[{"role":"user","parts":[{"text":"..."}]},{"role":"model","parts":[{"text":"..."}]}]}
    output_pairs_df["contents"] = output_pairs_df.apply(lambda row: [{"role":"user","parts":[{"text": row["question"]}]},{"role":"model","parts":[{"text": row["answer"]}]}], axis=1)


    # Test train split
    df_train, df_test = train_test_split(output_pairs_df, test_size=0.1, random_state=42)
    df_train[["text"]].to_csv(os.path.join(OUTPUT_FOLDER, "train.csv"), index = False)
    df_test[["text"]].to_csv(os.path.join(OUTPUT_FOLDER, "test.csv"), index = False)

    # Gemini : Max numbers of examples in validation dataset: 256
    df_test = df_test[:256]

    # JSONL
    with open(os.path.join(OUTPUT_FOLDER, "train.jsonl"), "w") as json_file:
        json_file.write(df_train[["contents"]].to_json(orient='records', lines=True))
    with open(os.path.join(OUTPUT_FOLDER, "test.jsonl"), "w") as json_file:
        json_file.write(df_test[["contents"]].to_json(orient='records', lines=True))


def upload():
    print("upload()")

    storage_client = storage.Client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    timeout = 300

    data_files = glob.glob(os.path.join(OUTPUT_FOLDER, "*.jsonl")) + glob.glob(os.path.join(OUTPUT_FOLDER, "*.csv"))
    data_files.sort()
    
    # Upload
    for index, data_file in enumerate(data_files):
        filename = os.path.basename(data_file)
        destination_blob_name = os.path.join("llm-finetune-dataset", filename)
        blob = bucket.blob(destination_blob_name)
        print("Uploading file:", data_file, destination_blob_name)
        blob.upload_from_filename(data_file, timeout=timeout)
    

def main(args=None):
    print("CLI Arguments:", args)

    if args.generate:
        generate()
    
    if args.save_prompt:
        save_prompt()

    if args.prepare:
        prepare()
      
    if args.upload:
        upload()


if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal '--help', it will provide the description
    parser = argparse.ArgumentParser(description="CLI")

    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate data",
    )
    parser.add_argument(
        "--prepare",
        action="store_true",
        help="Prepare data",
    )
    parser.add_argument(
        "--save_prompt",
        action="store_true",
        help="Save the system instruction, the prompt, and the number of iterations",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload data to bucket",
    )

    args = parser.parse_args()

    main(args)