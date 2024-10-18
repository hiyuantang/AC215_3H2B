#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

# Read the settings file
source env.dev

# Set vairables
export PERSISTENT_DIR=$(pwd)/../persistent-folder/
export REPO_DIR=$(cd "$BASE_DIR/.." && pwd)

# Create the network if we don't have it yet
docker network inspect llm-rag-network >/dev/null 2>&1 || docker network create llm-rag-network

# List of directories and their corresponding image names
directories=("llm-rag" "gemini-finetuner" "data-versioning" "dataset-creator")
images=("llm-rag-cli" "gemini-finetuner" "data-versioning" "dataset-creator")

# Iterate through the directories and images
for i in "${!directories[@]}"; do
  dir="${directories[$i]}"
  image="${images[$i]}"

  # Change into the project directory
  cd "$dir" || { echo "Directory $dir not found"; exit 1; }
  
  # Build the Docker image
  docker build -t "$image" -f Dockerfile .
  
  # Return to the initial directory
  cd - > /dev/null
done

# Run All Containers
# docker-compose up