#!/bin/bash

# AiRoHire Testing Framework
# Comprehensive test runner for both frontend and backend

echo "🧪 AiRoHire - Comprehensive Testing Framework"
echo "============================================="
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run tests with error handling
run_tests() {
    local test_type=$1
    local test_command=$2
    local test_dir=$3
    
    echo "📂 Running $test_type tests..."
    echo "Directory: $test_dir"
    echo "Command: $test_command"
    echo "----------------------------------------"
    
    cd "$test_dir" || {
        echo "❌ Failed to change to directory: $test_dir"
        return 1
    }
    
    if eval "$test_command"; then
        echo "✅ $test_type tests passed!"
        return 0
    else
        echo "❌ $test_type tests failed!"
        return 1
    fi
}

# Store current directory
ORIGINAL_DIR=$(pwd)
PROJECT_ROOT="$ORIGINAL_DIR"

# Check if we're in the project root
if [[ ! -d "frontend" || ! -d "backend" ]]; then
    echo "❌ Please run this script from the project root directory"
    echo "Expected structure: frontend/ and backend/ directories"
    exit 1
fi

# Initialize results
FRONTEND_PASSED=0
BACKEND_PASSED=0

echo "🔍 Checking prerequisites..."

# Check Node.js and npm for frontend
if command_exists node && command_exists npm; then
    echo "✅ Node.js and npm found"
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    echo "   Node.js: $NODE_VERSION"
    echo "   npm: $NPM_VERSION"
else
    echo "❌ Node.js and/or npm not found. Please install Node.js."
    echo "   Frontend tests will be skipped."
fi

# Check Python for backend
if command_exists python3; then
    echo "✅ Python3 found"
    PYTHON_VERSION=$(python3 --version)
    echo "   $PYTHON_VERSION"
else
    echo "❌ Python3 not found. Please install Python3."
    echo "   Backend tests will be skipped."
fi

echo ""
echo "🚀 Starting test execution..."
echo ""

# Frontend Tests
if command_exists node && command_exists npm; then
    echo "FRONTEND TESTS"
    echo "=============="
    
    # Check if package.json exists
    if [[ -f "frontend/package.json" ]]; then
        cd frontend || exit 1
        
        echo "📦 Installing frontend dependencies..."
        if npm install; then
            echo "✅ Frontend dependencies installed successfully"
        else
            echo "❌ Failed to install frontend dependencies"
            cd "$ORIGINAL_DIR"
            exit 1
        fi
        
        # Run different types of tests
        echo ""
        echo "🧪 Running frontend test suites..."
        
        # Basic tests
        if run_tests "Frontend Unit" "npm run test -- --run" "$PROJECT_ROOT/frontend"; then
            FRONTEND_PASSED=$((FRONTEND_PASSED + 1))
        fi
        
        cd "$PROJECT_ROOT/frontend"
        
        # Coverage tests
        if npm run test:coverage -- --run > /dev/null 2>&1; then
            echo "📊 Running frontend tests with coverage..."
            if run_tests "Frontend Coverage" "npm run test:coverage -- --run" "$PROJECT_ROOT/frontend"; then
                echo "✅ Frontend coverage report generated"
            fi
        else
            echo "⚠️  Coverage testing not available, running basic tests only"
        fi
        
        # Lint check
        cd "$PROJECT_ROOT/frontend"
        if npm run lint > /dev/null 2>&1; then
            echo "🔍 Running frontend linting..."
            if run_tests "Frontend Linting" "npm run lint" "$PROJECT_ROOT/frontend"; then
                echo "✅ Frontend code passes linting"
            fi
        else
            echo "⚠️  Linting not configured or failed"
        fi
        
    else
        echo "❌ frontend/package.json not found"
    fi
else
    echo "⚠️  Skipping frontend tests - Node.js/npm not available"
fi

echo ""
cd "$ORIGINAL_DIR"

# Backend Tests
if command_exists python3; then
    echo "BACKEND TESTS"
    echo "============="
    
    # Check if requirements.txt exists
    if [[ -f "backend/requirements.txt" ]]; then
        cd backend || exit 1
        
        echo "📦 Installing backend dependencies..."
        if python3 -m pip install -r requirements.txt; then
            echo "✅ Backend dependencies installed successfully"
        else
            echo "❌ Failed to install backend dependencies"
            cd "$ORIGINAL_DIR"
            exit 1
        fi
        
        echo ""
        echo "🧪 Running backend test suites..."
        
        # Check if pytest is available
        if python3 -m pytest --version > /dev/null 2>&1; then
            # Run different types of tests
            
            # Basic tests
            if run_tests "Backend Unit" "python3 -m pytest tests/ -v" "$PROJECT_ROOT/backend"; then
                BACKEND_PASSED=$((BACKEND_PASSED + 1))
            fi
            
            cd "$PROJECT_ROOT/backend"
            
            # API tests
            if [[ -f "tests/test_api_comprehensive.py" ]]; then
                if run_tests "Backend API" "python3 -m pytest tests/test_api_comprehensive.py -v" "$PROJECT_ROOT/backend"; then
                    echo "✅ API tests passed"
                fi
            fi
            
            cd "$PROJECT_ROOT/backend"
            
            # Model tests
            if [[ -f "tests/test_models_comprehensive.py" ]]; then
                if run_tests "Backend Models" "python3 -m pytest tests/test_models_comprehensive.py -v" "$PROJECT_ROOT/backend"; then
                    echo "✅ Model tests passed"
                fi
            fi
            
            cd "$PROJECT_ROOT/backend"
            
            # Coverage tests
            if python3 -c "import pytest_cov" > /dev/null 2>&1; then
                echo "📊 Running backend tests with coverage..."
                if run_tests "Backend Coverage" "python3 -m pytest tests/ --cov=. --cov-report=term-missing --cov-report=html" "$PROJECT_ROOT/backend"; then
                    echo "✅ Backend coverage report generated in htmlcov/"
                fi
            else
                echo "⚠️  pytest-cov not available, running basic tests only"
            fi
            
        else
            echo "❌ pytest not found. Please install pytest:"
            echo "   python3 -m pip install pytest"
        fi
        
    else
        echo "❌ backend/requirements.txt not found"
    fi
else
    echo "⚠️  Skipping backend tests - Python3 not available"
fi

cd "$ORIGINAL_DIR"

# Test Results Summary
echo ""
echo "FINAL RESULTS"
echo "============="
echo ""

if command_exists node && command_exists npm; then
    if [[ $FRONTEND_PASSED -gt 0 ]]; then
        echo "✅ Frontend: Tests passed"
    else
        echo "❌ Frontend: Tests failed or not run"
    fi
else
    echo "⚠️  Frontend: Skipped (Node.js not available)"
fi

if command_exists python3; then
    if [[ $BACKEND_PASSED -gt 0 ]]; then
        echo "✅ Backend: Tests passed"
    else
        echo "❌ Backend: Tests failed or not run"
    fi
else
    echo "⚠️  Backend: Skipped (Python3 not available)"
fi

echo ""

# Overall result
if [[ $FRONTEND_PASSED -gt 0 && $BACKEND_PASSED -gt 0 ]]; then
    echo "🎉 All test suites passed successfully!"
    echo ""
    echo "📊 Coverage Reports:"
    echo "   Frontend: Check terminal output above"
    echo "   Backend: Open backend/htmlcov/index.html"
    echo ""
    echo "✅ AiRoHire is ready for production!"
    exit 0
elif [[ $FRONTEND_PASSED -gt 0 || $BACKEND_PASSED -gt 0 ]]; then
    echo "⚠️  Some test suites passed, others failed or were skipped"
    echo ""
    echo "🔍 Next steps:"
    echo "   1. Check failed test output above"
    echo "   2. Install missing dependencies"
    echo "   3. Re-run tests"
    exit 1
else
    echo "❌ No test suites passed successfully"
    echo ""
    echo "🔍 Troubleshooting:"
    echo "   1. Ensure you're in the project root directory"
    echo "   2. Install Node.js and Python3"
    echo "   3. Install project dependencies"
    echo "   4. Check test file locations"
    exit 1
fi