#!/bin/bash

# Development environment setup script for File Collaboration Backend

set -e  # Exit on any error

echo "🚀 Setting up development environment for File Collaboration Backend..."

# Check if Python 3.8+ is available
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created!"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install development dependencies
echo "📦 Installing development dependencies..."
pip install -r requirements-dev.txt

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
pre-commit install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔧 Creating .env file..."
    cat > .env << EOF
# Database Configuration
POSTGRES_SERVER=localhost
POSTGRES_PORT=5433
POSTGRES_USER=postgres
POSTGRES_PASSWORD=12345678
POSTGRES_DB=file_collaboration_db

# Security
SECRET_KEY=your-secret-key-here-change-in-production

# API Configuration
API_V1_STR=/api/v1
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]

# Environment
ENVIRONMENT=local

# Superuser
FIRST_SUPERUSER=admin@example.com
FIRST_SUPERUSER_PASSWORD=admin123
EOF
    echo "✅ .env file created!"
else
    echo "✅ .env file already exists"
fi

# Initialize database
echo "🗄️ Applying database migrations..."
alembic upgrade head

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "📋 Available commands:"
echo "  make run         - Start the development server"
echo "  make test        - Run tests"
echo "  make lint        - Run linting"
echo "  make format      - Format code"
echo "  make check       - Run all quality checks"
echo ""
echo "🌐 Once running, visit:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo ""
echo "🚀 To start development:"
echo "  make run"
