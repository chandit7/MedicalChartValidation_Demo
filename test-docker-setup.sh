#!/bin/bash
# Docker Setup Test Script
# Tests the Docker configuration for Medical Chart Validation System

set -e

echo "=========================================="
echo "Docker Setup Test Script"
echo "Medical Chart Validation System"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to print test result
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
        ((TESTS_FAILED++))
    fi
}

# Test 1: Check Docker is installed
echo "Test 1: Checking Docker installation..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    test_result 0 "Docker is installed ($DOCKER_VERSION)"
else
    test_result 1 "Docker is not installed"
    echo "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Test 2: Check Docker Compose is installed
echo ""
echo "Test 2: Checking Docker Compose installation..."
if docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version)
    test_result 0 "Docker Compose is installed ($COMPOSE_VERSION)"
else
    test_result 1 "Docker Compose is not installed"
    exit 1
fi

# Test 3: Check Docker daemon is running
echo ""
echo "Test 3: Checking Docker daemon..."
if docker info &> /dev/null; then
    test_result 0 "Docker daemon is running"
else
    test_result 1 "Docker daemon is not running"
    echo "Please start Docker Desktop"
    exit 1
fi

# Test 4: Check required files exist
echo ""
echo "Test 4: Checking required files..."
FILES=("Dockerfile" "docker-compose.yml" ".dockerignore" ".env.example" "medchart_demo/docker-entrypoint.sh")
ALL_FILES_EXIST=0

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file exists"
    else
        echo "  ✗ $file missing"
        ALL_FILES_EXIST=1
    fi
done

test_result $ALL_FILES_EXIST "All required files present"

# Test 5: Check .env file
echo ""
echo "Test 5: Checking environment configuration..."
if [ -f ".env" ]; then
    test_result 0 ".env file exists"
else
    echo -e "${YELLOW}⚠ WARNING${NC}: .env file not found"
    echo "  Creating .env from .env.example..."
    cp .env.example .env
    test_result 0 ".env file created from template"
fi

# Test 6: Check data directory
echo ""
echo "Test 6: Checking data directory..."
if [ -d "data" ]; then
    test_result 0 "data directory exists"
else
    echo "  Creating data directory..."
    mkdir -p data
    test_result 0 "data directory created"
fi

# Test 7: Check sample data
echo ""
echo "Test 7: Checking sample data..."
if [ -d "medchart_demo/sample_data" ]; then
    SAMPLE_COUNT=$(ls -1 medchart_demo/sample_data/*.txt 2>/dev/null | wc -l)
    if [ $SAMPLE_COUNT -ge 5 ]; then
        test_result 0 "Sample data directory exists with $SAMPLE_COUNT files"
    else
        test_result 1 "Sample data directory exists but missing files (found $SAMPLE_COUNT, expected 5+)"
    fi
else
    test_result 1 "Sample data directory not found"
fi

# Test 8: Validate docker-compose.yml
echo ""
echo "Test 8: Validating docker-compose.yml..."
if docker compose config &> /dev/null; then
    test_result 0 "docker-compose.yml is valid"
else
    test_result 1 "docker-compose.yml has errors"
fi

# Test 9: Check port availability
echo ""
echo "Test 9: Checking port 8501 availability..."
if command -v netstat &> /dev/null; then
    if netstat -an | grep -q ":8501"; then
        echo -e "${YELLOW}⚠ WARNING${NC}: Port 8501 is already in use"
        echo "  You may need to stop the existing service or change the port in docker-compose.yml"
        test_result 1 "Port 8501 is available"
    else
        test_result 0 "Port 8501 is available"
    fi
else
    echo "  Skipping port check (netstat not available)"
    test_result 0 "Port check skipped"
fi

# Test 10: Check disk space
echo ""
echo "Test 10: Checking disk space..."
AVAILABLE_SPACE=$(df -h . | awk 'NR==2 {print $4}')
echo "  Available space: $AVAILABLE_SPACE"
test_result 0 "Disk space check complete"

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "You're ready to start the application:"
    echo "  docker compose up -d"
    echo ""
    echo "Then open: http://localhost:8501"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo "Please fix the issues above before proceeding"
    exit 1
fi

# Made with Bob
