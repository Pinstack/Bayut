#!/bin/bash

# Code Quality Check Script for Bayut.sa Property Scraper
# This script runs all code quality tools in sequence

set -e  # Exit on any error

echo "🔍 Running Code Quality Checks..."
echo "=================================="

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Virtual environment not activated. Please run: source .venv/bin/activate"
    exit 1
fi

# Install dev dependencies if not already installed
echo "📦 Installing development dependencies..."
pip install -e ".[dev]" > /dev/null 2>&1 || pip install ruff black flake8 vulture pytest pytest-asyncio

echo ""
echo "🔧 Running Ruff (fast linter + formatter)..."
ruff check src/ tests/ bayut.py || {
    echo "❌ Ruff found issues. Run 'ruff check --fix src/ tests/ bayut.py' to auto-fix some issues."
    exit 1
}
echo "✅ Ruff linting passed!"

echo ""
echo "🎨 Running Ruff format check..."
ruff format --check src/ tests/ bayut.py || {
    echo "❌ Ruff found formatting issues. Run 'ruff format src/ tests/ bayut.py' to fix."
    exit 1
}
echo "✅ Ruff formatting passed!"

echo ""
echo "🐍 Running Flake8 (comprehensive linter)..."
flake8 src/ tests/ bayut.py || {
    echo "❌ Flake8 found issues."
    exit 1
}
echo "✅ Flake8 passed!"

echo ""
echo "🦅 Running Vulture (dead code detection)..."
vulture src/ tests/ bayut.py --min-confidence 80 || {
    echo "⚠️  Vulture found potential dead code (this is often a false positive)."
    echo "   Review the output above and remove truly unused code."
}
echo "✅ Vulture completed!"

echo ""
echo "🧪 Running Pytest (tests)..."
pytest tests/ -v || {
    echo "❌ Tests failed."
    exit 1
}
echo "✅ All tests passed!"

echo ""
echo "🎉 All code quality checks passed!"
echo "==================================" 