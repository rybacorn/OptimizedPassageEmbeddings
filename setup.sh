#!/bin/bash

# Setup script for OptimizedPassageEmbeddings
# This script installs all dependencies and verifies the installation

set -e  # Exit on any error

echo "════════════════════════════════════════════════════════════════"
echo "  OptimizedPassageEmbeddings - Setup Script"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check Python version
echo "🔍 Checking Python version..."
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "❌ ERROR: Python 3.8+ required, but found Python $PYTHON_VERSION"
    echo "   Please upgrade Python and try again."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ ERROR: pyproject.toml not found"
    echo "   Please run this script from the OptimizedPassageEmbeddings directory:"
    echo "   cd OptimizedPassageEmbeddings"
    echo "   ./setup.sh"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies from requirements.txt..."
echo ""
pip install -r requirements.txt

echo ""
echo "📦 Installing package in editable mode..."
echo ""
pip install -e .

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "  Installation Complete - Verifying..."
echo "════════════════════════════════════════════════════════════════"
echo ""

# Test if passage-embed command exists
if command -v passage-embed &> /dev/null; then
    echo "✅ SUCCESS! The 'passage-embed' command is installed and ready."
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  Quick Start Guide"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "1️⃣  Create a queries.txt file with your target keywords:"
    echo "    echo \"ai video generator\" > queries.txt"
    echo "    echo \"best ai video generator\" >> queries.txt"
    echo "    echo \"free ai video generator\" >> queries.txt"
    echo ""
    echo "2️⃣  Run your first analysis:"
    echo ""
    echo "    passage-embed analyze \\"
    echo "      --client \"https://yoursite.com/page\" \\"
    echo "      --competitor \"https://competitor.com/page\" \\"
    echo "      --query-file \"queries.txt\""
    echo ""
    echo "3️⃣  View results:"
    echo "    Open outputs/embedding_visualization.html in your browser"
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "📚 For detailed documentation, see:"
    echo "   - SETUP.md (installation guide)"
    echo "   - README.md (usage examples)"
    echo ""
    echo "💡 Test your installation:"
    echo "   passage-embed --help"
    echo ""
else
    echo "⚠️  WARNING: 'passage-embed' command not found in PATH"
    echo ""
    echo "This can happen if your Python bin directory isn't in PATH."
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo "  Alternative Usage Method"
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "You can still use the tool with this command format:"
    echo ""
    echo "    python -m src.passage_embed.cli analyze \\"
    echo "      --client \"https://yoursite.com/page\" \\"
    echo "      --competitor \"https://competitor.com/page\" \\"
    echo "      --query-file \"queries.txt\""
    echo ""
    echo "════════════════════════════════════════════════════════════════"
    echo ""
    echo "💡 Test with:"
    echo "   python -m src.passage_embed.cli --help"
    echo ""
fi

echo "✨ Setup complete!"
echo ""

