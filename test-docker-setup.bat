@echo off
REM Docker Setup Test Script for Windows
REM Tests the Docker configuration for Medical Chart Validation System

echo ==========================================
echo Docker Setup Test Script
echo Medical Chart Validation System
echo ==========================================
echo.

set TESTS_PASSED=0
set TESTS_FAILED=0

REM Test 1: Check Docker is installed
echo Test 1: Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    docker --version
    echo [PASS] Docker is installed
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] Docker is not installed
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    set /a TESTS_FAILED+=1
    goto :summary
)

REM Test 2: Check Docker Compose is installed
echo.
echo Test 2: Checking Docker Compose installation...
docker compose version >nul 2>&1
if %errorlevel% equ 0 (
    docker compose version
    echo [PASS] Docker Compose is installed
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] Docker Compose is not installed
    set /a TESTS_FAILED+=1
    goto :summary
)

REM Test 3: Check Docker daemon is running
echo.
echo Test 3: Checking Docker daemon...
docker info >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] Docker daemon is running
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] Docker daemon is not running
    echo Please start Docker Desktop
    set /a TESTS_FAILED+=1
    goto :summary
)

REM Test 4: Check required files exist
echo.
echo Test 4: Checking required files...
set FILES_MISSING=0

if exist "Dockerfile" (
    echo   [OK] Dockerfile exists
) else (
    echo   [MISSING] Dockerfile
    set FILES_MISSING=1
)

if exist "docker-compose.yml" (
    echo   [OK] docker-compose.yml exists
) else (
    echo   [MISSING] docker-compose.yml
    set FILES_MISSING=1
)

if exist ".dockerignore" (
    echo   [OK] .dockerignore exists
) else (
    echo   [MISSING] .dockerignore
    set FILES_MISSING=1
)

if exist ".env.example" (
    echo   [OK] .env.example exists
) else (
    echo   [MISSING] .env.example
    set FILES_MISSING=1
)

if exist "medchart_demo\docker-entrypoint.sh" (
    echo   [OK] docker-entrypoint.sh exists
) else (
    echo   [MISSING] docker-entrypoint.sh
    set FILES_MISSING=1
)

if %FILES_MISSING% equ 0 (
    echo [PASS] All required files present
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] Some required files are missing
    set /a TESTS_FAILED+=1
)

REM Test 5: Check .env file
echo.
echo Test 5: Checking environment configuration...
if exist ".env" (
    echo [PASS] .env file exists
    set /a TESTS_PASSED+=1
) else (
    echo [WARNING] .env file not found
    echo   Creating .env from .env.example...
    copy .env.example .env >nul
    if %errorlevel% equ 0 (
        echo [PASS] .env file created from template
        set /a TESTS_PASSED+=1
    ) else (
        echo [FAIL] Could not create .env file
        set /a TESTS_FAILED+=1
    )
)

REM Test 6: Check data directory
echo.
echo Test 6: Checking data directory...
if exist "data\" (
    echo [PASS] data directory exists
    set /a TESTS_PASSED+=1
) else (
    echo   Creating data directory...
    mkdir data
    if %errorlevel% equ 0 (
        echo [PASS] data directory created
        set /a TESTS_PASSED+=1
    ) else (
        echo [FAIL] Could not create data directory
        set /a TESTS_FAILED+=1
    )
)

REM Test 7: Check sample data
echo.
echo Test 7: Checking sample data...
if exist "medchart_demo\sample_data\" (
    dir /b medchart_demo\sample_data\*.txt 2>nul | find /c /v "" > temp_count.txt
    set /p SAMPLE_COUNT=<temp_count.txt
    del temp_count.txt
    if %SAMPLE_COUNT% geq 5 (
        echo [PASS] Sample data directory exists with %SAMPLE_COUNT% files
        set /a TESTS_PASSED+=1
    ) else (
        echo [FAIL] Sample data directory exists but missing files
        set /a TESTS_FAILED+=1
    )
) else (
    echo [FAIL] Sample data directory not found
    set /a TESTS_FAILED+=1
)

REM Test 8: Validate docker-compose.yml
echo.
echo Test 8: Validating docker-compose.yml...
docker compose config >nul 2>&1
if %errorlevel% equ 0 (
    echo [PASS] docker-compose.yml is valid
    set /a TESTS_PASSED+=1
) else (
    echo [FAIL] docker-compose.yml has errors
    set /a TESTS_FAILED+=1
)

REM Test 9: Check port availability
echo.
echo Test 9: Checking port 8501 availability...
netstat -an | findstr ":8501" >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARNING] Port 8501 is already in use
    echo   You may need to stop the existing service or change the port
    set /a TESTS_FAILED+=1
) else (
    echo [PASS] Port 8501 is available
    set /a TESTS_PASSED+=1
)

REM Test 10: Check disk space
echo.
echo Test 10: Checking disk space...
for /f "tokens=3" %%a in ('dir /-c ^| findstr /C:"bytes free"') do set FREE_SPACE=%%a
echo   Free space: %FREE_SPACE% bytes
echo [PASS] Disk space check complete
set /a TESTS_PASSED+=1

:summary
REM Summary
echo.
echo ==========================================
echo Test Summary
echo ==========================================
echo Tests Passed: %TESTS_PASSED%
echo Tests Failed: %TESTS_FAILED%
echo.

if %TESTS_FAILED% equ 0 (
    echo [SUCCESS] All tests passed!
    echo.
    echo You're ready to start the application:
    echo   docker compose up -d
    echo.
    echo Then open: http://localhost:8501
    exit /b 0
) else (
    echo [ERROR] Some tests failed
    echo Please fix the issues above before proceeding
    exit /b 1
)

@REM Made with Bob
