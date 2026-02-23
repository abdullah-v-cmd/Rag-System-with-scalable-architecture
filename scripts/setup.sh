#!/bin/bash

# Setup development environment

echo "🛠️  Setting up development environment..."

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with your OpenAI API key"
fi

# Make scripts executable
chmod +x scripts/*.sh

# Create necessary directories
mkdir -p backend/uploads backend/vector_db backend/logs

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Update .env with your OpenAI API key"
echo "   2. Run './scripts/start.sh' to start all services"
echo "   3. Access the application at http://localhost:3000"
