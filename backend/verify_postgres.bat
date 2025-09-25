@echo off
echo Verifying PostgreSQL Installation
echo ================================

echo Testing PostgreSQL installation...
psql --version
if %ERRORLEVEL% neq 0 (
    echo ERROR: PostgreSQL not found in PATH
    echo Please install PostgreSQL first
    pause
    exit /b 1
)

echo ✓ PostgreSQL is installed

echo.
echo Setting environment variable...
set DATABASE_URL=postgresql://postgres:testpass@localhost:5432/hospital_test
echo ✓ Environment variable set for this session

echo.
echo Creating test database...
createdb -U postgres hospital_test
if %ERRORLEVEL% neq 0 (
    echo WARNING: Database creation failed or database already exists
    echo This might be okay if database already exists
)

echo.
echo Testing database connection...
psql -U postgres -d hospital_test -c "SELECT version();"
if %ERRORLEVEL% neq 0 (
    echo ERROR: Cannot connect to database
    echo Please check PostgreSQL is running and password is correct
    pause
    exit /b 1
)

echo ✓ Database connection successful

echo.
echo Running production database integration test...
python test_production_integration.py

echo.
echo Verification complete!
pause