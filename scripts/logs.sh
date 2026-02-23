#!/bin/bash

# View logs for all services or specific service

if [ -z "$1" ]; then
    echo "📋 Viewing logs for all services..."
    docker-compose logs -f
else
    echo "📋 Viewing logs for $1..."
    docker-compose logs -f $1
fi
