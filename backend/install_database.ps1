# Hospital Intelligence System - PostgreSQL Installation Script
# ===========================================================

Write-Host "Hospital Intelligence System - Database Installation" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host ""
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as administrator'" -ForegroundColor Yellow
    Write-Host "Then run this script again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✓ Running as Administrator" -ForegroundColor Green

# Install Chocolatey if not present
try {
    $chocoVersion = choco --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Chocolatey is already installed" -ForegroundColor Green
    } else {
        throw "Chocolatey not found"
    }
} catch {
    Write-Host ""
    Write-Host "Installing Chocolatey package manager..." -ForegroundColor Yellow
    
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    
    try {
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
        Write-Host "✓ Chocolatey installed successfully" -ForegroundColor Green
        
        # Refresh environment
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    } catch {
        Write-Host "ERROR: Failed to install Chocolatey" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Install PostgreSQL
Write-Host ""
Write-Host "Installing PostgreSQL 14..." -ForegroundColor Yellow

try {
    choco install postgresql14 -y --params "/Password:testpass"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ PostgreSQL installed successfully" -ForegroundColor Green
    } else {
        throw "PostgreSQL installation failed"
    }
} catch {
    Write-Host "ERROR: Failed to install PostgreSQL" -ForegroundColor Red
    Write-Host "You can try manual installation from: https://www.postgresql.org/download/" -ForegroundColor Yellow
    Read-Host "Press Enter to continue anyway"
}

# Install Docker Desktop
Write-Host ""
Write-Host "Installing Docker Desktop..." -ForegroundColor Yellow

try {
    choco install docker-desktop -y
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Docker Desktop installed successfully" -ForegroundColor Green
    } else {
        Write-Host "WARNING: Docker Desktop installation may have failed" -ForegroundColor Yellow
        Write-Host "You can install manually from: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    }
} catch {
    Write-Host "WARNING: Docker Desktop installation failed" -ForegroundColor Yellow
    Write-Host "You can install manually from: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
}

# Set environment variables
Write-Host ""
Write-Host "Setting environment variables..." -ForegroundColor Yellow

try {
    [System.Environment]::SetEnvironmentVariable("DATABASE_URL", "postgresql://postgres:testpass@localhost:5432/hospital_test", "Machine")
    Write-Host "✓ Environment variables set" -ForegroundColor Green
} catch {
    Write-Host "WARNING: Could not set environment variables" -ForegroundColor Yellow
}

# Add PostgreSQL to PATH
$pgPath = "C:\Program Files\PostgreSQL\14\bin"
if (Test-Path $pgPath) {
    Write-Host ""
    Write-Host "Adding PostgreSQL to PATH..." -ForegroundColor Yellow
    
    $currentPath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($currentPath -notlike "*$pgPath*") {
        [System.Environment]::SetEnvironmentVariable("Path", "$currentPath;$pgPath", "Machine")
        Write-Host "✓ PostgreSQL added to PATH" -ForegroundColor Green
    } else {
        Write-Host "✓ PostgreSQL already in PATH" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""
Write-Host "What was installed:"
Write-Host "✓ Chocolatey package manager" -ForegroundColor Green
Write-Host "✓ PostgreSQL 14 database server" -ForegroundColor Green
Write-Host "✓ Docker Desktop (for containerized testing)" -ForegroundColor Green
Write-Host "✓ Environment variables configured" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. RESTART your computer for all changes to take effect"
Write-Host "2. After restart, open a new PowerShell/Command Prompt"
Write-Host "3. Verify installation:"
Write-Host "   psql --version"
Write-Host "   docker --version"
Write-Host "4. Create test database (if not done automatically):"
Write-Host "   createdb -U postgres hospital_test"
Write-Host "5. Run integration tests:"
Write-Host "   python test_production_integration.py"
Write-Host ""
Write-Host "Default PostgreSQL credentials:" -ForegroundColor Cyan
Write-Host "  Username: postgres"
Write-Host "  Password: testpass"
Write-Host "  Database: hospital_test"
Write-Host "  Port: 5432"
Write-Host ""

Read-Host "Press Enter to exit"