@echo off
echo Hospital Intelligence System - PostgreSQL Installation
echo =====================================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Please run as Administrator
    echo Right-click Command Prompt and select "Run as administrator"
    pause
    exit /b 1
)

echo Running as Administrator...
echo.

REM Install Chocolatey
echo Installing Chocolatey package manager...
powershell -Command "& {Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))}"

REM Refresh environment
call "%ALLUSERSPROFILE%\chocolatey\bin\RefreshEnv.cmd"

echo.
echo Installing PostgreSQL...
choco install postgresql14 -y --params "/Password:testpass"

echo.
echo Installing Docker Desktop...
choco install docker-desktop -y

echo.
echo Setting environment variables...
setx DATABASE_URL "postgresql://postgres:testpass@localhost:5432/hospital_test" /M

echo.
echo Adding PostgreSQL to PATH...
setx PATH "%PATH%;C:\Program Files\PostgreSQL\14\bin" /M

echo.
echo ===============================================
echo Installation Complete!
echo ===============================================
echo.
echo IMPORTANT: RESTART YOUR COMPUTER NOW!
echo.
echo After restart:
echo 1. Open new Command Prompt
echo 2. Run: psql --version
echo 3. Run: docker --version
echo 4. Run: createdb -U postgres hospital_test
echo 5. Run: python test_production_integration.py
echo.
echo Database credentials:
echo   Username: postgres
echo   Password: testpass
echo   Database: hospital_test
echo.
pause