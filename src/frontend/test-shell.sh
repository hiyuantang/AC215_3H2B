#!/bin/bash

echo "Container is running!!!"

# Build the image
docker build -t frontend .

# Run tests
docker run --rm -e NODE_ENV=development frontend npm run test
