#!/bin/bash

# AutoStream AI - Quick Start Script
# This script helps you get started quickly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Python
    if command -v python3 &> /dev/null; then
        print_status "Python 3 is installed: $(python3 --version)"
    else
        print_error "Python 3 is not installed. Please install Python 3.11+"
        exit 1
    fi
    
    # Check Node.js
    if command -v node &> /dev/null; then
        print_status "Node.js is installed: $(node --version)"
    else
        print_warning "Node.js is not installed. Frontend won't work without it."
    fi
    
    # Check FFmpeg
    if command -v ffmpeg &> /dev/null; then
        print_status "FFmpeg is installed: $(ffmpeg -version | head -n1)"
    else
        print_warning "FFmpeg is not installed. Video rendering may not work."
        echo "  Install with: sudo apt install ffmpeg (Ubuntu/Debian)"
        echo "  Or: brew install ffmpeg (macOS)"
    fi
    
    # Check Git
    if command -v git &> /dev/null; then
        print_status "Git is installed"
    else
        print_error "Git is not installed"
        exit 1
    fi
}

# Setup backend
setup_backend() {
    print_header "Setting Up Backend"
    
    cd backend
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -q -r requirements.txt
    
    cd ..
    print_status "Backend setup complete"
}

# Setup frontend
setup_frontend() {
    if ! command -v node &> /dev/null; then
        print_warning "Skipping frontend setup (Node.js not found)"
        return
    fi
    
    print_header "Setting Up Frontend"
    
    cd frontend
    
    # Install npm dependencies
    if [ ! -d "node_modules" ]; then
        print_status "Installing npm dependencies..."
        npm install
    else
        print_status "Dependencies already installed"
    fi
    
    cd ..
    print_status "Frontend setup complete"
}

# Start Ollama (optional)
start_ollama() {
    print_header "Ollama Setup"
    
    if command -v ollama &> /dev/null; then
        print_status "Ollama is installed"
        
        if pgrep -x "ollama" > /dev/null; then
            print_status "Ollama is already running"
        else
            print_warning "Ollama is not running"
            read -p "Start Ollama now? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                print_status "Starting Ollama..."
                ollama serve &
                sleep 5
                
                # Pull default model
                print_status "Pulling Llama 3 model (this may take a while)..."
                ollama pull llama3
                print_status "Llama 3 model ready"
            fi
        fi
    else
        print_warning "Ollama is not installed"
        echo "  Install from: https://ollama.com/"
        echo "  Script generation will use fallback mode"
    fi
}

# Start the application
start_application() {
    print_header "Starting AutoStream AI"
    
    echo "Select startup method:"
    echo "1) Development mode (separate terminals)"
    echo "2) Production mode (Docker)"
    echo "3) Exit"
    
    read -p "Enter your choice (1-3): " choice
    
    case $choice in
        1)
            print_status "Starting in development mode..."
            echo ""
            echo "Starting backend on port 8000..."
            (cd backend && source venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000) &
            BACKEND_PID=$!
            
            sleep 3
            
            if ! command -v node &> /dev/null; then
                print_warning "Frontend requires Node.js. Starting backend only."
                echo ""
                echo "Backend running at: http://localhost:8000"
                echo "API docs at: http://localhost:8000/docs"
            else
                echo ""
                echo "Starting frontend on port 5173..."
                (cd frontend && npm run dev) &
                FRONTEND_PID=$!
                
                sleep 5
                echo ""
                echo "════════════════════════════════════════════════════════════"
                echo -e "${GREEN}AutoStream AI is running!${NC}"
                echo "════════════════════════════════════════════════════════════"
                echo ""
                echo "  Frontend: http://localhost:5173"
                echo "  Backend:  http://localhost:8000"
                echo "  API Docs: http://localhost:8000/docs"
                echo ""
                print_warning "Press Ctrl+C to stop the servers"
                echo ""
                
                # Wait for user interrupt
                trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
                wait
            fi
            ;;
        2)
            print_status "Starting with Docker Compose..."
            if command -v docker &> /dev/null; then
                docker-compose up -d
                echo ""
                echo "════════════════════════════════════════════════════════════"
                echo -e "${GREEN}AutoStream AI is running via Docker!${NC}"
                echo "════════════════════════════════════════════════════════════"
                echo ""
                echo "  Frontend: http://localhost:5173"
                echo "  Backend:  http://localhost:8000"
                echo "  Ollama:   http://localhost:11434"
                echo "  Firecrawl: http://localhost:3002"
            else
                print_error "Docker is not installed"
            fi
            ;;
        3)
            print_status "Exiting..."
            exit 0
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
}

# Show help
show_help() {
    echo "AutoStream AI - Quick Start Script"
    echo ""
    echo "Usage: ./start.sh [command]"
    echo ""
    echo "Commands:"
    echo "  setup       Check prerequisites and install dependencies"
    echo "  start       Start the application"
    echo "  backend     Setup and start backend only"
    echo "  frontend    Setup and start frontend only"
    echo "  ollama      Setup Ollama for local LLM"
    echo "  help        Show this help message"
    echo ""
}

# Main entry point
main() {
    cd "$(dirname "$0")"
    
    case "${1:-start}" in
        setup)
            check_prerequisites
            setup_backend
            setup_frontend
            start_ollama
            ;;
        start)
            check_prerequisites
            start_application
            ;;
        backend)
            setup_backend
            print_status "Starting backend..."
            cd backend && source venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000
            ;;
        frontend)
            setup_frontend
            print_status "Starting frontend..."
            cd frontend && npm run dev
            ;;
        ollama)
            start_ollama
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
