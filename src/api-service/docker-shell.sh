#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

# Define some environment variables
export IMAGE_NAME="tripee-app-api-service"
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../../secrets/
export PERSISTENT_DIR=$(pwd)/../../persistent-folder/
export GCP_PROJECT="ac215-3h2b-yuantang" # CHANGE TO YOUR PROJECT ID
export CHROMADB_HOST="llm-rag-chromadb"
export CHROMADB_PORT=8000

# Create the network if we don't have it yet
docker network inspect tripee-network >/dev/null 2>&1 || docker network create tripee-network

# Build the image based on the Dockerfile
#docker build -t $IMAGE_NAME -f Dockerfile .
# M1/2 chip macs use this line
docker build -t $IMAGE_NAME --platform=linux/arm64/v8 -f Dockerfile .

# Run the container
docker run --rm --name $IMAGE_NAME -ti \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-v "$PERSISTENT_DIR":/persistent \
-p 9000:9000 \
-e GOOGLE_APPLICATION_CREDENTIALS=/secrets/llm-service-account-key.json \
-e GCP_PROJECT=$GCP_PROJECT \
-e CHROMADB_HOST=$CHROMADB_HOST \
-e CHROMADB_PORT=$CHROMADB_PORT \
--network tripee-network \
$IMAGE_NAME