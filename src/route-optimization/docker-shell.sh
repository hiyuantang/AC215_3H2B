#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

# Define the image name
export IMAGE_NAME="route-optimization"

# Build the Docker image using the Dockerfile in the current directory
docker build -t $IMAGE_NAME -f Dockerfile .

# Run the container
docker run --rm --name $IMAGE_NAME -ti $IMAGE_NAME
