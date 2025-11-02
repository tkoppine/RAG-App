#!/bin/bash

# =============================================================================
# ArXiv Research Assistant - Setup Script
# =============================================================================

set -e  # Exit on any error

echo "🔬 ArXiv Research Assistant Setup"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.10+ is available
check_python() {
    print_status "Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
            print_success "Python $PYTHON_VERSION found"
            PYTHON_CMD="python3"
        else
            print_error "Python 3.10+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.10+"
        exit 1
    fi
}

# Create virtual environment
setup_venv() {
    print_status "Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    print_success "Dependencies installed"
}

# Setup environment configuration
setup_env() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_success "Environment file created from template"
        print_warning "Please edit .env file with your API keys and configuration"
    else
        print_warning ".env file already exists"
    fi
}

# Create required directories
setup_directories() {
    print_status "Creating required directories..."
    
    mkdir -p data logs media static
    
    print_success "Directories created"
}

# Django setup
setup_django() {
    print_status "Setting up Django..."
    
    cd llm-integration/llmproject
    
    # Generate Django secret key if needed
    if grep -q "your-secret-key-here" ../../.env; then
        print_status "Generating Django secret key..."
        SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
        sed -i.bak "s/your-secret-key-here/$SECRET_KEY/" ../../.env
        rm ../../.env.bak 2>/dev/null || true
        print_success "Django secret key generated"
    fi
    
    # Run migrations
    python manage.py migrate
    
    # Collect static files
    python manage.py collectstatic --noinput
    
    cd ../..
    
    print_success "Django setup completed"
}

# Validate configuration
validate_setup() {
    print_status "Validating setup..."
    
    python config/settings.py
    
    print_success "Setup validation completed"
}

# Main setup process
main() {
    echo "Starting setup process..."
    echo
    
    check_python
    setup_venv
    install_dependencies
    setup_env
    setup_directories
    setup_django
    validate_setup
    
    echo
    print_success "🎉 Setup completed successfully!"
    echo
    echo "Next steps:"
    echo "1. Edit .env file with your API keys"
    echo "2. Add your paper data to the data/ directory"
    echo "3. Run: python src/storage/faiss_manager.py --input data/embeddings.json"
    echo "4. Start the application: python llm-integration/llmproject/manage.py runserver"
    echo
    echo "For Docker deployment: docker-compose up"
    echo
}

# Run main function
main "$@"