import os
import argparse
import pandas as pd
import json
import time
import glob
from google.cloud import storage, aiplatform
import vertexai
from vertexai.preview.tuning import sft
from vertexai.generative_models import GenerativeModel, GenerationConfig

# Setup
GCP_PROJECT = os.environ["GCP_PROJECT"]
GCP_LOCATION = os.environ["GCP_LOCATION"]
TRAIN_DATASET = "gs://strict-format-dataset/llm-finetune-dataset/train.jsonl" # Replace with your dataset
VALIDATION_DATASET = "gs://strict-format-dataset/llm-finetune-dataset/test.jsonl" # Replace with your dataset
GENERATIVE_SOURCE_MODEL = "gemini-1.5-flash-002" # gemini-1.5-pro-002
# Configuration settings for the content generation
generation_config = {
    "max_output_tokens": 3000,  # Maximum number of tokens for output
    "temperature": 0.75,  # Control randomness in output
    "top_p": 0.95,  # Use nucleus sampling
}

vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)

def train(wait_for_job=False):
    print("train()")

    # Supervised Fine Tuning
    sft_tuning_job = sft.train(
        source_model=GENERATIVE_SOURCE_MODEL,
        train_dataset=TRAIN_DATASET,
        validation_dataset=VALIDATION_DATASET,
        epochs=6, # change to 2-3
        adapter_size=4,
        learning_rate_multiplier=1.0,
        tuned_model_display_name="strict-format",
    )
    print("Training job started. Monitoring progress...\n\n")
    
    # Wait and refresh
    time.sleep(60)
    sft_tuning_job.refresh()
    
    if wait_for_job:
        print("Check status of tuning job:")
        print(sft_tuning_job)
        while not sft_tuning_job.has_ended:
            time.sleep(60)
            sft_tuning_job.refresh()
            print("Job in progress...")

    print(f"Tuned model name: {sft_tuning_job.tuned_model_name}")
    print(f"Tuned model endpoint name: {sft_tuning_job.tuned_model_endpoint_name}")
    print(f"Experiment: {sft_tuning_job.experiment}")


def chat():
    print("chat()")
    MODEL_ENDPOINT = "projects/184619367894/locations/us-central1/endpoints/8964855962443710464" # Finetuned model
    
    generative_model = GenerativeModel(MODEL_ENDPOINT)

    query = '''Location:  New Orleans, Days: 4, month: April, type: Boring. How can I craft a concise itinerary with only days and locations that makes me feel bored in New Orleans in April?'''
    
    print("query: ",query)
    response = generative_model.generate_content(
        [query],  # Input prompt
        generation_config=generation_config,  # Configuration settings
        stream=False,  # Enable streaming for responses
    )
    generated_text = response.text
    print("Fine-tuned LLM Response:", generated_text)


def delete_model():
    """
    Delete a Model resource.
    Args:
        model_id: The ID of the model to delete. Parent resource name of the model is also accepted.
        project: The project.
        location: The region name.
    Returns
        None.
    """
    # Initialize the client.
    aiplatform.init(project=GCP_PROJECT, location=GCP_LOCATION)

    # Get the model with the ID 'model_id'. The parent_name of Model resource can be also
    # 'projects/<your-project-id>/locations/<your-region>/models/<your-model-id>'
    model = aiplatform.Model(model_name="projects/682865987385/locations/us-central1/models/6409824035957374976")

    # Delete the model.
    model.delete()

def delete_hyperparameter_tuning_job():
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.JobServiceClient(client_options=client_options)
    name = client.hyperparameter_tuning_job_path(
        project="682865987385",
        location=GCP_LOCATION,
        hyperparameter_tuning_job="5638299578605240320",
    )
    response = client.delete_hyperparameter_tuning_job(name=name)
    print("Long running operation:", response.operation.name)
    delete_hyperparameter_tuning_job_response = response.result(timeout=300)
    print(
        "delete_hyperparameter_tuning_job_response:",
        delete_hyperparameter_tuning_job_response,
    )

     

def main(args=None):
    print("CLI Arguments:", args)

    if args.train:
        train()
    
    if args.chat:
        chat()
    
    if args.delete_model:
        delete_model()
    
    if args.delete_hyperparameter_tuning_job:
        delete_hyperparameter_tuning_job()


if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal '--help', it will provide the description
    parser = argparse.ArgumentParser(description="CLI")

    parser.add_argument(
        "--train",
        action="store_true",
        help="Train model",
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Chat with model",
    )
    parser.add_argument(
        "--delete_model",
        action="store_true",
        help="delete model",
    )
    parser.add_argument(
        "--delete_hyperparameter_tuning_job",
        action="store_true",
        help="delete tuning job",
    )

    args = parser.parse_args()

    main(args)