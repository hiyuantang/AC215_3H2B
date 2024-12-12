#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

if [ ! -f "./.env.local" ]; then
  echo ".env.local file not found! Please create this and assign your Google Maps API key to NEXT_PUBLIC_GOOGLE_MAPS_API_KEY."
  exit 1
fi

# Fetch key from .env.local
export $(grep -v '^#' ./.env.local | xargs)

# Define the image name
export IMAGE_NAME="trip-advisor-ui"

# Build the Docker image using the Dockerfile in the current directory
docker build --build-arg NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=$NEXT_PUBLIC_GOOGLE_MAPS_API_KEY -t $IMAGE_NAME .

# Run the container
docker run -p 3000:3000 $IMAGE_NAME
