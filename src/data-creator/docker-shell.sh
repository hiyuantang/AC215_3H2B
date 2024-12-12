#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../../secrets/

export IMAGE_NAME="dataset-creator"

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .

# Run Container
docker run --rm --name $IMAGE_NAME -ti \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
$IMAGE_NAME