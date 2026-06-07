#!/bin/bash
# Setup script for Website Defacement Detection System
# For macOS and Linux

set -e  # Exit on error

echo "=========================================="
echo "Website Defacement Detection System Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Found: $PYTHON_VERSION"
else
    echo "✗ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Create project structure
echo ""
echo "Creating project directories..."
mkdir -p src data logs
echo "✓ Directories created"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠  Virtual environment already exists"
    read -p "Remove and recreate? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo "✓ Virtual environment recreated"
    else
        echo "Using existing virtual environment"
    fi
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"

# Install dependencies
echo ""
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
    echo "✓ Dependencies installed from requirements.txt"
else
    echo "requirements.txt not found, installing core packages..."
    pip install flask requests watchdog colorama --quiet
    echo "✓ Core packages installed"
fi

# Verify installation
echo ""
echo "Verifying installation..."
python3 -c "import flask, requests, watchdog, colorama" 2>/dev/null && echo "✓ All packages verified" || echo "✗ Some packages failed to install"

# Set executable permissions for scripts
echo ""
echo "Setting executable permissions..."
chmod +x src/*.py 2>/dev/null || true
echo "✓ Permissions set"

# Create .gitignore
echo ""
echo "Creating .gitignore..."
cat > .gitignore << EOF
# Virtual Environment
venv/
env/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Data and Logs
data/*.json
logs/*.json
logs/*.txt
!data/.gitkeep
!logs/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
echo "✓ .gitignore created"

# Summary
echo ""
echo "=========================================="
echo "Setup Complete! ✓"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Start the vulnerable server (Terminal 1):"
echo "   python src/vulnerable_server.py"
echo ""
echo "3. Start the detection monitor (Terminal 2):"
echo "   python src/detection_monitor.py"
echo ""
echo "4. Run attack simulator (Terminal 3):"
echo "   python src/attack_simulator.py"
echo ""
echo "For more information, see README.md"
echo "=========================================="




if SHA256(current_value) != SHA256(baseline_value):
      raise defacement alert