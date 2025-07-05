#!/bin/bash

# German Economic Insights Dashboard - Quick Start Script
# This script automates the setup and launch process

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Banner
echo -e "${BLUE}"
echo "🏛️  German Economic Insights Dashboard"
echo "======================================="
echo -e "${NC}"

# Check if Python 3.8+ is installed
print_info "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    print_error "Python $PYTHON_VERSION found, but Python $REQUIRED_VERSION or higher is required."
    exit 1
fi

print_status "Python $PYTHON_VERSION found"

# Check if pip is installed
print_info "Checking pip..."
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip."
    exit 1
fi
print_status "pip found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_status "pip upgraded"

# Install requirements
print_info "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
    print_status "Dependencies installed"
else
    print_error "requirements.txt not found!"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found"
    
    # Create .env file
    cat > .env << EOF
GEMINI_API_KEY=AIzaSyB2TCDx9ZkjQrgBM5ibX9jvx5uzkF8bQAc
DATABASE_URL=sqlite:///./dashboard.db
DEBUG=True
HOST=0.0.0.0
PORT=8000
EOF
    
    print_info "Created .env file with default settings"
    print_warning "Please edit .env file and add your Gemini API key:"
    print_info "  1. Get API key from: https://makersuite.google.com/app/apikey"
    print_info "  2. Replace 'your_gemini_api_key_here' with your actual API key"
    
    # Ask if user wants to continue without API key
    echo ""
    read -p "Continue without API key? (AI features will be disabled) [y/N]: " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Please configure your API key and run this script again."
        exit 0
    fi
else
    print_status ".env file found"
fi

# Create necessary directories
print_info "Creating directories..."
mkdir -p uploads static templates services data
print_status "Directories created"

# Check if main.py exists
if [ ! -f "main.py" ]; then
    print_error "main.py not found! Please ensure all project files are present."
    exit 1
fi

# Final setup complete
print_status "Setup complete!"
echo ""
print_info "🚀 Starting the dashboard..."
print_info "   URL: http://localhost:8000"
print_info "   Press Ctrl+C to stop"
echo ""

# Start the application
python main.py