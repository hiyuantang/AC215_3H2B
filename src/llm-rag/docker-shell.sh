#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

# Read the settings file
source ../env.dev

# Set vairables
export PERSISTENT_DIR=$(pwd)/../persistent-folder/
export IMAGE_NAME="llm-rag-cli"

# Create the network if we don't have it yet
docker network inspect tripee-network >/dev/null 2>&1 || docker network create tripee-network

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .

# Run All Containers
docker-compose run --rm --service-ports $IMAGE_NAME

# # Run Container
# docker run --rm --name $IMAGE_NAME -ti \
# -v "$BASE_DIR":/app \
# -v "$SECRETS_DIR":/secrets \
# -v "$PERSISTENT_DIR":/persistent \
# -e GOOGLE_APPLICATION_CREDENTIALS=$GOOGLE_APPLICATION_CREDENTIALS \
# -e GCP_PROJECT=$GCP_PROJECT \
# $IMAGE_NAME