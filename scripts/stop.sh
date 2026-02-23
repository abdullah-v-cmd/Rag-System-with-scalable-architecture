#!/bin/bash

# Stop all services

echo "🛑 Stopping RAG Document Intelligence Platform..."

docker-compose down

echo "✅ All services stopped!"
echo ""
echo "💡 To remove all data (volumes), run:"
echo "   docker-compose down -v"
