#!/bin/bash
# Medical Chart Validation System - Docker Entrypoint Script
# Initializes the container environment before starting the application

set -e

echo "=========================================="
echo "Medical Chart Validation System"
echo "Docker Container Initialization"
echo "=========================================="

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# =============================================================================
# STEP 1: Environment Validation
# =============================================================================
log "Step 1: Validating environment..."

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
log "Python version: $PYTHON_VERSION"

# Check if required directories exist
if [ ! -d "/app/data" ]; then
    log "Creating data directory..."
    mkdir -p /app/data
fi

if [ ! -d "/app/sample_data" ]; then
    log "WARNING: sample_data directory not found!"
    log "Make sure to mount sample_data volume in docker-compose.yml"
else
    log "Sample data directory found: $(ls -la /app/sample_data | wc -l) files"
fi

# =============================================================================
# STEP 2: Database Initialization
# =============================================================================
log "Step 2: Initializing database..."

# Set database path from environment or use default
DB_PATH="${DB_PATH:-/app/data/medchart.db}"
log "Database path: $DB_PATH"

# Check if database exists
if [ -f "$DB_PATH" ]; then
    log "Database already exists. Skipping initialization."
    # Get record count
    RECORD_COUNT=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM results;" 2>/dev/null || echo "0")
    log "Current records in database: $RECORD_COUNT"
else
    log "Database not found. Creating new database..."
    python -c "import db; db.init_db()" 2>&1
    if [ $? -eq 0 ]; then
        log "Database initialized successfully!"
    else
        log "ERROR: Database initialization failed!"
        exit 1
    fi
fi

# =============================================================================
# STEP 3: Verify Dependencies
# =============================================================================
log "Step 3: Verifying Python dependencies..."

# Check critical packages
REQUIRED_PACKAGES=("streamlit" "pandas" "pdfplumber")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python -c "import $package" 2>/dev/null; then
        log "✓ $package installed"
    else
        log "✗ $package NOT installed"
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    log "ERROR: Missing required packages: ${MISSING_PACKAGES[*]}"
    log "Please rebuild the Docker image"
    exit 1
fi

# Check optional packages
OPTIONAL_PACKAGES=("groq" "mcp")
for package in "${OPTIONAL_PACKAGES[@]}"; do
    if python -c "import $package" 2>/dev/null; then
        log "✓ $package installed (optional)"
    else
        log "ℹ $package not installed (optional - features may be limited)"
    fi
done

# =============================================================================
# STEP 4: Environment Variables Check
# =============================================================================
log "Step 4: Checking environment variables..."

if [ -n "$GROQ_API_KEY" ] && [ "$GROQ_API_KEY" != "your_groq_api_key_here" ]; then
    log "✓ GROQ_API_KEY is set (AI analytics enabled)"
else
    log "ℹ GROQ_API_KEY not set (AI analytics will be limited)"
fi

# =============================================================================
# STEP 5: File Permissions
# =============================================================================
log "Step 5: Checking file permissions..."

# Ensure data directory is writable
if [ -w "/app/data" ]; then
    log "✓ Data directory is writable"
else
    log "WARNING: Data directory is not writable!"
    log "Database operations may fail"
fi

# =============================================================================
# STEP 6: Health Check Setup
# =============================================================================
log "Step 6: Setting up health check..."

# Create a simple health check endpoint test
if command_exists curl; then
    log "✓ curl available for health checks"
else
    log "WARNING: curl not available - health checks may not work"
fi

# =============================================================================
# STEP 7: Display Configuration
# =============================================================================
log "=========================================="
log "Configuration Summary:"
log "=========================================="
log "Working Directory: $(pwd)"
log "Database Path: $DB_PATH"
log "Streamlit Port: ${STREAMLIT_SERVER_PORT:-8501}"
log "Server Address: ${STREAMLIT_SERVER_ADDRESS:-0.0.0.0}"
log "Python Version: $PYTHON_VERSION"
log "User: $(whoami)"
log "=========================================="

# =============================================================================
# STEP 8: Start Application
# =============================================================================
log "Starting application..."
log "=========================================="

# Execute the command passed to the container
exec "$@"

# Made with Bob
