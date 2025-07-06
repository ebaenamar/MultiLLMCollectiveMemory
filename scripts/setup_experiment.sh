#!/bin/bash

# Multi-LLM Collective Memory Benchmark Setup Script
# This script sets up the complete experimental environment

set -e  # Exit on any error

echo "🚀 Setting up Multi-LLM Collective Memory Benchmark"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Python 3.8+ is available
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
            print_status "Python $PYTHON_VERSION found"
        else
            print_error "Python 3.8+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.8+"
        exit 1
    fi
}

# Check if Docker is available
check_docker() {
    if command -v docker &> /dev/null; then
        print_status "Docker found"
        if command -v docker-compose &> /dev/null; then
            print_status "Docker Compose found"
        else
            print_warning "Docker Compose not found. Some features may not work."
        fi
    else
        print_warning "Docker not found. Manual setup required for memory services."
    fi
}

# Create virtual environment
setup_venv() {
    if [ ! -d "venv" ]; then
        echo "Creating Python virtual environment..."
        python3 -m venv venv
        print_status "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_status "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
    print_status "Pip upgraded"
}

# Install Python dependencies
install_dependencies() {
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
    print_status "Dependencies installed"
}

# Create necessary directories
create_directories() {
    echo "Creating project directories..."
    
    directories=(
        "results"
        "memory_data"
        "logs"
        "analysis_output"
        "exports"
        "temp"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
    done
    
    print_status "Directories created"
}

# Setup environment file
setup_env() {
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_warning "Created .env from template. Please edit with your API keys."
            echo "   Especially set your OPENAI_API_KEY"
        else
            print_error ".env.example not found"
            exit 1
        fi
    else
        print_status ".env file already exists"
    fi
}

# Test basic imports
test_imports() {
    echo "Testing Python imports..."
    
    python3 -c "
import sys
sys.path.append('.')

try:
    from memory_systems import BaseMemorySystem, SharedMemorySystem
    from agents import BaseSpecializedAgent, AgentOrchestrator
    print('✅ Core imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        print_status "Import tests passed"
    else
        print_error "Import tests failed"
        exit 1
    fi
}

# Setup Docker services (optional)
setup_docker() {
    if command -v docker-compose &> /dev/null; then
        echo "Would you like to start Docker services (Redis, ChromaDB)? [y/N]"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            echo "Starting Docker services..."
            docker-compose up -d redis chromadb
            print_status "Docker services started"
            
            # Wait for services to be ready
            echo "Waiting for services to be ready..."
            sleep 10
            print_status "Services should be ready"
        fi
    fi
}

# Run quick validation
run_validation() {
    echo "Running quick validation..."
    
    # Test memory systems
    python3 -c "
import sys
sys.path.append('.')

from memory_systems import NoMemorySystem, SharedMemorySystem
from memory_systems.base_memory import MemoryEntry

# Test NoMemorySystem
no_mem = NoMemorySystem()
entry = MemoryEntry('test', 'test content', 'test_agent', {})
no_mem.store(entry)
print('✅ NoMemorySystem test passed')

# Test SharedMemorySystem
shared_mem = SharedMemorySystem('./temp/test_shared.json')
shared_mem.store(entry)
retrieved = shared_mem.retrieve('test')
assert len(retrieved) > 0
print('✅ SharedMemorySystem test passed')
"
    
    if [ $? -eq 0 ]; then
        print_status "Validation tests passed"
    else
        print_error "Validation tests failed"
        exit 1
    fi
}

# Main setup function
main() {
    echo "Starting setup process..."
    echo
    
    # Run checks and setup
    check_python
    check_docker
    setup_venv
    install_dependencies
    create_directories
    setup_env
    test_imports
    setup_docker
    run_validation
    
    echo
    echo "🎉 Setup completed successfully!"
    echo "=================================================="
    echo
    echo "Next steps:"
    echo "1. Edit .env file with your API keys (especially OPENAI_API_KEY)"
    echo "2. Run quick demo: python quick_start.py"
    echo "3. Run full benchmark: python experiments/run_benchmark.py"
    echo "4. Analyze results: python evaluation/analyze_results.py"
    echo
    echo "For Docker users:"
    echo "- Start all services: docker-compose up -d"
    echo "- View logs: docker-compose logs -f"
    echo "- Stop services: docker-compose down"
    echo
    echo "Documentation:"
    echo "- README.md: Project overview and usage"
    echo "- paper/research_paper.md: Detailed methodology"
    echo "- evaluation/evaluation_prompts.md: Evaluation framework"
    echo
    print_status "Ready to run experiments!"
}

# Run main function
main "$@"
