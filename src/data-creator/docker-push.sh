#!/bin/bash

set -e

# Build and Push
DOCKERHUB_USERNAME="hiyt"
IMAGE_NAME="tripee-dataset-creator"
TAG="0.2"
FULL_IMAGE_NAME="$DOCKERHUB_USERNAME/$IMAGE_NAME:$TAG"
echo "Building image"
docker buildx build --platform linux/amd64 -t $FULL_IMAGE_NAME -f Dockerfile .
docker login
docker push $FULL_IMAGE_NAME