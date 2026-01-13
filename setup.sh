#!/bin/bash

# AI Research Publisher - Setup Script

echo "🚀 Setting up AI Research Publisher..."
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"

# Initialize project
echo "🏗️  Initializing project structure..."
python main.py init
echo "✓ Project initialized"

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "📝 IMPORTANT: Edit .env and add your PERPLEXITY_API_KEY"
    echo "   Get your API key from: https://www.perplexity.ai/settings/api"
    echo ""
else
    echo "✓ .env file already exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env and add your PERPLEXITY_API_KEY"
echo "   2. Run: source venv/bin/activate"
echo "   3. Test: python main.py fetch --source arxiv"
echo "   4. Generate: python main.py generate --count 2"
echo ""
echo "📖 Read DEVELOPMENT.md for detailed guide"
echo ""
