#!/bin/bash

# AiRoHire Docker Setup Script
# This script helps you get the entire AiRoHire system running with Docker

set -e

echo "🚀 AiRoHire Docker Setup"
echo "========================"
echo ""

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker and try again."
        exit 1
    fi
    echo "✅ Docker is running"
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1; then
        if ! docker compose version > /dev/null 2>&1; then
            echo "❌ Docker Compose is not available. Please install Docker Compose."
            exit 1
        else
            DOCKER_COMPOSE_CMD="docker compose"
        fi
    else
        DOCKER_COMPOSE_CMD="docker-compose"
    fi
    echo "✅ Docker Compose is available"
}

# Function to clean up existing containers
cleanup() {
    echo "🧹 Cleaning up existing containers..."
    $DOCKER_COMPOSE_CMD down --volumes --remove-orphans 2>/dev/null || true
    docker system prune -f > /dev/null 2>&1 || true
    echo "✅ Cleanup completed"
}

# Function to build and start services
start_services() {
    echo "🏗️  Building and starting services..."
    echo "This may take a few minutes on first run..."
    
    # Build images
    $DOCKER_COMPOSE_CMD build --no-cache
    
    # Start services
    $DOCKER_COMPOSE_CMD up -d postgres
    echo "⏳ Waiting for PostgreSQL to be ready..."
    sleep 10
    
    # Run database setup
    $DOCKER_COMPOSE_CMD up db-setup
    
    # Start remaining services
    $DOCKER_COMPOSE_CMD up -d backend frontend
    
    # Optional: Start nginx proxy
    read -p "🌐 Do you want to start the Nginx reverse proxy? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        $DOCKER_COMPOSE_CMD up -d nginx
        echo "✅ Nginx proxy started"
    fi
}

# Function to show service status
show_status() {
    echo ""
    echo "📊 Service Status:"
    echo "=================="
    $DOCKER_COMPOSE_CMD ps
    echo ""
    echo "🌐 Service URLs:"
    echo "==============="
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8000"
    echo "API Documentation: http://localhost:8000/docs"
    echo "Database: localhost:5432"
    
    if $DOCKER_COMPOSE_CMD ps nginx | grep -q "Up"; then
        echo "Nginx Proxy: http://localhost:80"
        echo "  - Frontend: http://localhost"
        echo "  - Backend: http://localhost/api/"
    fi
}

# Function to show logs
show_logs() {
    echo ""
    echo "📋 Recent Logs:"
    echo "==============="
    $DOCKER_COMPOSE_CMD logs --tail=10
}

# Function to run development mode
dev_mode() {
    echo "🔧 Starting in development mode..."
    
    # Copy development environment
    if [[ -f ".env.development" ]]; then
        cp .env.development .env
        echo "✅ Development environment loaded"
    fi
    
    # Start with hot reload
    $DOCKER_COMPOSE_CMD -f docker-compose.yml -f docker-compose.dev.yml up --build
}

# Function to run production mode
prod_mode() {
    echo "🚀 Starting in production mode..."
    
    # Copy production environment
    if [[ -f ".env.production" ]]; then
        cp .env.production .env
        echo "✅ Production environment loaded"
    fi
    
    start_services
}

# Main script
main() {
    check_docker
    check_docker_compose
    
    echo "🎯 Choose deployment mode:"
    echo "1) Development (with hot reload)"
    echo "2) Production (optimized)"
    echo "3) Clean setup (remove existing data)"
    echo "4) Show status only"
    echo "5) Show logs"
    echo "6) Stop all services"
    
    read -p "Enter your choice (1-6): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            dev_mode
            ;;
        2)
            prod_mode
            show_status
            ;;
        3)
            cleanup
            prod_mode
            show_status
            ;;
        4)
            show_status
            ;;
        5)
            show_logs
            ;;
        6)
            echo "⏹️  Stopping all services..."
            $DOCKER_COMPOSE_CMD down
            echo "✅ All services stopped"
            ;;
        *)
            echo "❌ Invalid option"
            exit 1
            ;;
    esac
}

# Help function
show_help() {
    echo "AiRoHire Docker Setup Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -d, --dev      Start in development mode"
    echo "  -p, --prod     Start in production mode"
    echo "  -c, --clean    Clean setup (remove existing data)"
    echo "  -s, --status   Show service status"
    echo "  -l, --logs     Show logs"
    echo "  --stop         Stop all services"
    echo ""
    echo "Interactive mode (no options): Choose from menu"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    -d|--dev)
        check_docker
        check_docker_compose
        dev_mode
        ;;
    -p|--prod)
        check_docker
        check_docker_compose
        prod_mode
        show_status
        ;;
    -c|--clean)
        check_docker
        check_docker_compose
        cleanup
        prod_mode
        show_status
        ;;
    -s|--status)
        show_status
        ;;
    -l|--logs)
        show_logs
        ;;
    --stop)
        check_docker_compose
        $DOCKER_COMPOSE_CMD down
        echo "✅ All services stopped"
        ;;
    "")
        main
        ;;
    *)
        echo "❌ Unknown option: $1"
        show_help
        exit 1
        ;;
esac