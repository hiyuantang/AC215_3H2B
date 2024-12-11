#!/bin/bash

# set -e

export IMAGE_NAME="tripee-workflow"
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../../secrets/
export GCP_PROJECT="ac215-3h2b-yuantang"
export GCS_BUCKET_NAME="llm-strict-format-dataset"
export GCS_SERVICE_ACCOUNT="llm-service-account@ac215-3h2b-yuantang.iam.gserviceaccount.com"
export GCP_REGION="us-central1"

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME --platform=linux/amd64 -f Dockerfile .

# Run Container
docker run --rm --name $IMAGE_NAME -ti \
-v /var/run/docker.sock:/var/run/docker.sock \
-v "$BASE_DIR":/app \
-v "$SECRETS_DIR":/secrets \
-v "$BASE_DIR/../data-creator":/data-creator \
-v "$BASE_DIR/../gemini-finetuner":/gemini-finetuner \
-e GOOGLE_APPLICATION_CREDENTIALS=/secrets/llm-service-account-key.json \
-e GCP_PROJECT=$GCP_PROJECT \
-e GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
-e GCS_SERVICE_ACCOUNT=$GCS_SERVICE_ACCOUNT \
-e GCP_REGION=$GCP_REGION \
$IMAGE_NAME

