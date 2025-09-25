@echo off
REM Automated PostgreSQL Installation Script
REM ========================================

echo Hospital Intelligence System - Database Installation
echo =====================================================

echo.
echo This script will install PostgreSQL and Docker for database integration.
echo You need to run this as Administrator.
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause >nul

REM Check if running as administrator
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: This script must be run as Administrator
    echo Right-click Command Prompt and select "Run as administrator"
    echo Then run this script again.
    pause
    exit /b 1
)

echo ✓ Running as Administrator

REM Check if Chocolatey is installed
choco --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo Installing Chocolatey package manager...
    powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
    
    if %ERRORLEVEL% neq 0 (
        echo ERROR: Failed to install Chocolatey
        pause
        exit /b 1
    )
    
    echo ✓ Chocolatey installed successfully
    
    REM Refresh environment variables
    call refreshenv.cmd
) else (
    echo ✓ Chocolatey is already installed
)

REM Install PostgreSQL
echo.
echo Installing PostgreSQL 14...
choco install postgresql14 -y --params "/Password:testpass"

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install PostgreSQL
    echo You can try manual installation from: https://www.postgresql.org/download/
    pause
    exit /b 1
)

echo ✓ PostgreSQL installed successfully

REM Install Docker Desktop
echo.
echo Installing Docker Desktop...
choco install docker-desktop -y

if %ERRORLEVEL% neq 0 (
    echo WARNING: Docker Desktop installation may have failed
    echo You can install manually from: https://www.docker.com/products/docker-desktop/
) else (
    echo ✓ Docker Desktop installed successfully
)

REM Add PostgreSQL to PATH
echo.
echo Adding PostgreSQL to PATH...
setx PATH "%PATH%;C:\Program Files\PostgreSQL\14\bin" /M

echo ✓ PostgreSQL added to PATH

REM Create test database
echo.
echo Creating test database...
timeout /t 5 /nobreak >nul

"C:\Program Files\PostgreSQL\14\bin\createdb.exe" -U postgres -W hospital_test

if %ERRORLEVEL% neq 0 (
    echo WARNING: Database creation may have failed
    echo You can create it manually later
) else (
    echo ✓ Test database created
)

REM Set environment variable
echo.
echo Setting environment variables...
setx DATABASE_URL "postgresql://postgres:testpass@localhost:5432/hospital_test" /M

echo ✓ Environment variables set

echo.
echo ===============================================
echo Installation Complete!
echo ===============================================
echo.
echo What was installed:
echo ✓ Chocolatey package manager
echo ✓ PostgreSQL 14 database server
echo ✓ Docker Desktop (for containerized testing)
echo ✓ Test database: hospital_test
echo ✓ Default password: testpass
echo.
echo IMPORTANT: You need to RESTART your computer for all changes to take effect!
echo.
echo After restart, verify installation:
echo   psql --version
echo   docker --version
echo.
echo Then run the integration tests:
echo   python test_production_integration.py
echo.
echo Press any key to exit...
pause >nul