#!/bin/bash

# Oracle Cloud Deployment Script for GenX FX AI/ML Processing
set -e

echo "🚀 Deploying GenX FX AI/ML Processing to Oracle Cloud..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is available"
}

# Check if Docker Compose is installed
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Build and start services
deploy_services() {
    print_status "Building and starting services..."
    
    # Build images
    docker-compose -f docker-compose.oracle.yml build
    
    # Start services
    docker-compose -f docker-compose.oracle.yml up -d
    
    print_success "Services deployed successfully!"
}

# Check service status
check_status() {
    print_status "Checking service status..."
    
    docker-compose -f docker-compose.oracle.yml ps
    
    # Check if services are running
    if docker-compose -f docker-compose.oracle.yml ps | grep -q "Up"; then
        print_success "All services are running!"
    else
        print_error "Some services failed to start"
        exit 1
    fi
}

# Show service URLs
show_urls() {
    print_status "Service URLs:"
    echo "  🤖 AI Processor: http://localhost:8001"
    echo "  🧠 Model Server: http://localhost:8002"
    echo "  📊 Backtester: http://localhost:8003"
    echo "  🔴 Redis: localhost:6379"
}

# Main deployment function
main() {
    print_status "Starting Oracle Cloud deployment..."
    
    # Check prerequisites
    check_docker
    check_docker_compose
    
    # Deploy services
    deploy_services
    
    # Check status
    check_status
    
    # Show URLs
    show_urls
    
    print_success "Oracle Cloud deployment completed!"
    print_status "Next steps:"
    echo "1. Monitor logs: docker-compose -f docker-compose.oracle.yml logs -f"
    echo "2. Access AI processor at: http://localhost:8001"
    echo "3. Check model server at: http://localhost:8002"
    echo "4. Run backtests at: http://localhost:8003"
}

# Run main function
main "$@"