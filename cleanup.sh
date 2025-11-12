#!/bin/bash

# Cleanup script for Learning Mentor repository
# Run this before committing to ensure clean state

echo "🧹 Cleaning up repository..."
echo ""

# Remove Python cache files
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -not -path "./venv/*" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -not -path "./venv/*" -delete 2>/dev/null
find . -type f -name "*.pyo" -not -path "./venv/*" -delete 2>/dev/null
echo "✓ Python cache cleaned"

# Remove .DS_Store files (macOS)
echo "Removing .DS_Store files..."
find . -name ".DS_Store" -delete 2>/dev/null
echo "✓ .DS_Store files removed"

# Remove swap files
echo "Removing swap files..."
find . -name "*.swp" -delete 2>/dev/null
find . -name "*.swo" -delete 2>/dev/null
echo "✓ Swap files removed"

# Remove mypy cache
echo "Removing type checking cache..."
rm -rf .mypy_cache 2>/dev/null
echo "✓ Type checking cache removed"

# Remove pytest cache
echo "Removing pytest cache..."
rm -rf .pytest_cache 2>/dev/null
echo "✓ Pytest cache removed"

# Remove sentence transformers cache (if in project root)
echo "Removing AI model cache..."
rm -rf .cache 2>/dev/null
rm -rf .sentence_transformers 2>/dev/null
echo "✓ AI cache removed"

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "Run 'git status' to verify what will be committed"
