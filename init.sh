#!/bin/bash

TOKEN="$1"

# update code with upstream
git pull || {
    echo "failed to update project"
    exit 1
}

# Check if a container with the same name exists and stop and remove it
if docker ps -a --format '{{.Names}}' | grep -q "^price-alert"; then
    echo "Found the old Container...Removing!"
    docker stop price-alert
    docker rm priceee-alert
fi

# build docker image 
docker build -t price-alert:latest . || {
    echo "failed to build docker image"
    exit 1
}

# run docker image 
docker run -d --name price-alert -e TELEGRAM_TOKEN=$TOKEN price-alert:latest