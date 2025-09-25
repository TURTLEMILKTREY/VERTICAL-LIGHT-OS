@echo off
REM Setup PostgreSQL for Database Integration Testing
REM ================================================

echo Hospital Intelligence System - Database Setup
echo =============================================

echo.
echo Setting up PostgreSQL database for integration testing...
echo.

REM Check if Docker is available
docker --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop and try again
    pause
    exit /b 1
)

echo ✓ Docker is available

REM Stop and remove existing container if it exists
echo.
echo Cleaning up existing test database...
docker stop postgres-test >nul 2>&1
docker rm postgres-test >nul 2>&1

REM Start PostgreSQL container
echo.
echo Starting PostgreSQL test database...
docker run --name postgres-test ^
  -e POSTGRES_PASSWORD=testpass ^
  -e POSTGRES_DB=hospital_test ^
  -e POSTGRES_USER=postgres ^
  -p 5432:5432 ^
  -d postgres:14

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to start PostgreSQL container
    pause
    exit /b 1
)

echo ✓ PostgreSQL container started successfully

REM Wait for database to be ready
echo.
echo Waiting for database to be ready...
timeout /t 5 /nobreak >nul

REM Set environment variable
echo.
echo Setting environment variables...
set DATABASE_URL=postgresql://postgres:testpass@localhost:5432/hospital_test
echo ✓ DATABASE_URL set to: %DATABASE_URL%

REM Test connection
echo.
echo Testing database connection...
python -c "import asyncpg; import asyncio; asyncio.run(asyncpg.connect('postgresql://postgres:testpass@localhost:5432/hospital_test').then(lambda c: c.close()))" >nul 2>&1

if %ERRORLEVEL% neq 0 (
    echo WARNING: Could not immediately connect to database
    echo Database may still be starting up...
    echo Please wait a moment and run the integration test
) else (
    echo ✓ Database connection successful
)

echo.
echo ================================================
echo Database setup complete!
echo.
echo Connection details:
echo   Host: localhost
echo   Port: 5432
echo   Database: hospital_test
echo   Username: postgres
echo   Password: testpass
echo.
echo To run integration tests:
echo   python test_production_integration.py
echo.
echo To stop the database:
echo   docker stop postgres-test
echo.
echo To remove the database:
echo   docker rm postgres-test
echo ================================================

pause