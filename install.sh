#!/bin/bash

# YouTube Shorts Generator - Installation Script
# This script sets up the environment with locked dependency versions

echo "🎬 YouTube Shorts Generator - Setup Script"
echo "=========================================="

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python found: $(python --version)"

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

echo "✅ pip found: $(pip --version)"

# Install locked dependencies
echo ""
echo "📦 Installing locked dependencies..."
echo "This may take a few minutes..."

pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All dependencies installed successfully!"
    echo ""
    echo "🔧 Next steps:"
    echo "1. Copy .env.example to .env"
    echo "2. Fill in your API keys in the .env file:"
    echo "   - OPEN_API_KEY (OpenAI)"
    echo "   - FAL_API_KEY (Fal AI)" 
    echo "   - ELVEN_LABS_API_KEY (ElevenLabs)"
    echo "3. Run: python main.py \"Your topic here\""
    echo ""
    echo "📖 See readme.md for more detailed instructions."
else
    echo ""
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi
