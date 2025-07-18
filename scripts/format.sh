#!/bin/bash

# Code Formatting Script for Bayut.sa Property Scraper
# This script automatically formats code using Ruff (primary) and Black (backup)

set -e  # Exit on any error

echo "🎨 Formatting Code..."
echo "===================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Virtual environment not activated. Please run: source .venv/bin/activate"
    exit 1
fi

# Install dev dependencies if not already installed
echo "📦 Installing development dependencies..."
pip install -e ".[dev]" > /dev/null 2>&1 || pip install ruff black

echo ""
echo "🔧 Running Ruff (linting + auto-fix)..."
ruff check --fix src/ tests/ bayut.py
echo "✅ Ruff auto-fixes complete!"

echo ""
echo "🎨 Running Ruff (code formatting)..."
ruff format src/ tests/ bayut.py
echo "✅ Ruff formatting complete!"

echo ""
echo "🎨 Running Black (backup formatter for consistency)..."
black src/ tests/ bayut.py
echo "✅ Black formatting complete!"

echo ""
echo "🎉 Code formatting complete!"
echo "============================" 