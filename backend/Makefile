# Makefile for FastAPI app with virtual environment management

.PHONY: help venv install install-dev run clean test lint format check

# Default target
help:
	@echo "Available commands:"
	@echo "  make venv        - Create virtual environment"
	@echo "  make install     - Install production dependencies"
	@echo "  make install-dev - Install development dependencies"
	@echo "  make run         - Run the FastAPI app"
	@echo "  make test        - Run tests"
	@echo "  make lint        - Run linting checks"
	@echo "  make format      - Format code with black and isort"
	@echo "  make check       - Run all quality checks"
	@echo "  make clean       - Remove virtual environment"
	@echo "  make help        - Show this help"

# Create virtual environment
venv:
	@echo "🔧 Creating virtual environment..."
	python3 -m venv venv
	@echo "✅ Virtual environment created!"

# Install production dependencies
install: venv
	@echo "📦 Installing production dependencies..."
	venv/bin/pip install -r requirements.txt
	@echo "✅ Production dependencies installed!"

# Install development dependencies
install-dev: venv
	@echo "📦 Installing development dependencies..."
	venv/bin/pip install -r requirements-dev.txt
	@echo "✅ Development dependencies installed!"

# Run the app
run: install
	@echo "🚀 Starting FastAPI app..."
	@echo "🌐 App will be available at: http://localhost:8000"
	@echo "📖 API docs at: http://localhost:8000/docs"
	@echo "🔄 Press Ctrl+C to stop the server"
	@echo "----------------------------------------"
	venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
test: install-dev
	@echo "🧪 Running tests..."
	venv/bin/pytest

# Run linting
lint: install-dev
	@echo "🔍 Running linting checks..."
	venv/bin/flake8 app/
	venv/bin/mypy app/

# Format code
format: install-dev
	@echo "🎨 Formatting code..."
	venv/bin/black app/
	venv/bin/isort app/

# Auto-fix style only
fix: install-dev
	@echo "🛠 Auto-fixing code style..."
	venv/bin/black app/
	venv/bin/isort app/
# Run all quality checks
check: format lint test
	@echo "✅ All quality checks passed!"

# Clean up
clean:
	@echo "🧹 Removing virtual environment..."
	rm -rf venv
	@echo "✅ Virtual environment removed!"

# Quick start (create venv, install deps, and run)
start: run
