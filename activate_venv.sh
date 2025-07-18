#!/bin/bash
# Script to activate the virtual environment for Bayut scraper

echo "🚀 Activating Bayut scraper virtual environment..."
source .venv/bin/activate
echo "✅ Virtual environment activated!"
echo "📦 Installed packages:"
pip list
echo ""
echo "🐍 You can now run: python scrape_100_properties.py" 