#!/bin/bash

# Rural Business Simulator - Automated Setup Script
# This script sets up the entire application automatically

echo "🌾 Rural Business Simulator - Setup Script"
echo "==========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Create project directory structure
echo "📁 Creating project directories..."
mkdir -p .streamlit
mkdir -p data
mkdir -p utils
mkdir -p pages
mkdir -p backups

echo "✅ Directories created"
echo ""

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "✅ Virtual environment created and activated"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install streamlit>=1.28.0 requests>=2.31.0 python-dotenv>=1.0.0

echo "✅ Dependencies installed"
echo ""

# Create __init__.py for utils
echo "📝 Creating utils/__init__.py..."
cat > utils/__init__.py << 'EOF'
"""
Utils package for Rural Business Simulator
"""

from .ai_manager import AIManager
from .database import DatabaseManager

__all__ = ['AIManager', 'DatabaseManager']
EOF

echo "✅ Utils package initialized"
echo ""

# Create secrets template
echo "🔐 Creating secrets template..."
cat > .streamlit/secrets.toml.example << 'EOF'
# Copy this file to secrets.toml and add your actual API keys
# Never commit secrets.toml to version control!

# Choose ONE AI provider and add your key:

# Option 1: Hugging Face (FREE - Recommended)
HUGGINGFACE_API_KEY = "hf_your_api_key_here"

# Option 2: OpenAI (Paid)
# OPENAI_API_KEY = "sk-your_api_key_here"

# Option 3: Anthropic Claude (Paid)
# ANTHROPIC_API_KEY = "sk-ant-your_api_key_here"
EOF

echo "✅ Secrets template created"
echo ""

# Create .gitignore
echo "🚫 Creating .gitignore..."
cat > .gitignore << 'EOF'
.streamlit/secrets.toml
.env
data/
__pycache__/
*.pyc
venv/
.DS_Store
*.log
backups/
EOF

echo "✅ .gitignore created"
echo ""

# Create README
echo "📖 Creating README.md..."
cat > README.md << 'EOF'
# Rural Business Simulator

Educational platform for teaching entrepreneurship through gamified scenarios.

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Run the app: `streamlit run app.py`
3. Open browser at http://localhost:8501

## Setup AI (Optional)

1. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`
2. Add your API key from Hugging Face (free)
3. Restart the app

See full documentation for more details.
EOF

echo "✅ README created"
echo ""

echo "==========================================="
echo "✨ Setup Complete!"
echo "==========================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Copy all the code files (app.py, config.py, etc.) to this directory"
echo "2. (Optional) Configure AI by editing .streamlit/secrets.toml"
echo "3. Run the app:"
echo ""
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   venv\\Scripts\\activate"
else
    echo "   source venv/bin/activate"
fi
echo "   streamlit run app.py"
echo ""
echo "4. Open your browser to http://localhost:8501"
echo ""
echo "🎉 Happy Teaching!"
