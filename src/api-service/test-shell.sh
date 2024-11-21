#!/bin/bash

echo "Container is running!!!"

export GCP_PROJECT="ac215-3h2b-yuantang"
export CHROMADB_HOST="llm-rag-chromadb"
export CHROMADB_PORT=8000

# Build the image
docker build -t api-service .

# Run tests
docker run -it --rm \
    -e GCP_PROJECT=$GCP_PROJECT \
    -e CHROMADB_HOST=$CHROMADB_HOST \
    -e CHROMADB_PORT=$CHROMADB_PORT \
    -v "$(pwd):/app" \
    --entrypoint /bin/bash \
    api-service \
    -c "cd /app && PYTHONPATH=/app pipenv install --dev && PYTHONPATH=/app pipenv run pytest tests/ -v --cov=. --cov-report=xml"