#!/bin/bash

# Stop the existing Docker Compose stack
docker-compose -f docker-compose.prod-no-letsencrypt.yml -p danswer-stack down

# Check if the previous command was successful
if [ $? -eq 0 ]; then
    echo "Successfully stopped the stack. Proceeding to restart..."

    # Start the Docker Compose stack with build and force-recreate options
    docker-compose -f docker-compose.prod-no-letsencrypt.yml -p danswer-stack up -d --build --force-recreate
else
    echo "Failed to stop the stack. Aborting restart."
    exit 1
fi
