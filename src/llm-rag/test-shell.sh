#!/bin/bash

echo "Container is running!!!"

# Build the image
docker build -t llm-rag-cli .

# Run tests
docker run -it --rm \
    -v "$(pwd):/app" \
    --entrypoint /bin/bash \
    llm-rag-cli \
    -c "cd /app && PYTHONPATH=/app pipenv install --dev && PYTHONPATH=/app pipenv run pytest tests/ -v --cov=. --cov-report=term-missing"