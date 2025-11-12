#!/bin/bash

# Learning Mentor - Initial Setup Script
# Creates required directory structure and configuration files

set -e  # Exit on error

echo "🎓 Learning Mentor - Initial Setup"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create directory structure
echo "📁 Creating directory structure..."

# Create main directories
mkdir -p topics
mkdir -p daily_notes
mkdir -p docs

echo "${GREEN}✓${NC} Created topics/ directory"
echo "${GREEN}✓${NC} Created daily_notes/ directory"
echo "${GREEN}✓${NC} Created docs/ directory"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "🔑 Creating .env configuration file..."
    
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "${GREEN}✓${NC} Created .env from .env.example"
    else
        cat > .env << 'EOF'
# API Keys Configuration
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Ollama Configuration (for local models)
OLLAMA_MODEL=llama2
OLLAMA_HOST=http://localhost:11434

# Default LLM provider (options: openai, anthropic, ollama, google)
DEFAULT_LLM_PROVIDER=openai
EOF
        echo "${GREEN}✓${NC} Created .env file"
    fi
    
    echo "${YELLOW}⚠${NC}  Please edit .env and add your API keys"
else
    echo ""
    echo "${YELLOW}⚠${NC}  .env file already exists, skipping..."
fi

# Create Python virtual environment
echo ""
echo "🐍 Setting up Python virtual environment..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "${GREEN}✓${NC} Created virtual environment"
    
    # Activate venv and install dependencies
    echo ""
    echo "📦 Installing dependencies..."
    source venv/bin/activate
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt
    echo "${GREEN}✓${NC} Installed all dependencies"
else
    echo "${YELLOW}⚠${NC}  Virtual environment already exists, skipping..."
fi

# Make start script executable
echo ""
echo "🔧 Setting up executable scripts..."
chmod +x start_notes.sh
echo "${GREEN}✓${NC} Made start_notes.sh executable"

# Summary
echo ""
echo "=================================="
echo "${GREEN}✅ Setup Complete!${NC}"
echo "=================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Edit .env file with your API keys:"
echo "   ${YELLOW}nano .env${NC}"
echo ""
echo "2. (Optional) To use local models, install Ollama:"
echo "   ${YELLOW}brew install ollama${NC}"
echo "   ${YELLOW}ollama pull llama2${NC}"
echo ""
echo "3. Start taking notes:"
echo "   ${YELLOW}./start_notes.sh${NC}"
echo ""
echo "4. Or activate the virtual environment manually:"
echo "   ${YELLOW}source venv/bin/activate${NC}"
echo "   ${YELLOW}python scripts/interactive_note_system.py${NC}"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Complete user guide"
echo "   - PRODUCT_SPEC.md - Product vision & features"
echo "   - IMPLEMENTATION_ROADMAP.md - Development guide"
echo ""
echo "🆘 Need help? Check README.md or open an issue on GitHub"
echo ""
