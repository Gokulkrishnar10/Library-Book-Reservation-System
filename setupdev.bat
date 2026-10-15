@echo off
cd /d "%~dp0"

echo Setting up backend...
python -m venv env
if errorlevel 1 (
    echo Error creating virtual environment.
    exit /b 1
)

call env\Scripts\activate
if errorlevel 1 (
    echo Error activating virtual environment.
    exit /b 1
)

echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error installing requirements.
    exit /b 1
)

echo Running database migrations...
alembic upgrade head
if errorlevel 1 (
    echo Error running migrations.
    exit /b 1
)

echo Seeding database...
python seed_db.py
if errorlevel 1 (
    echo Error seeding database.
    exit /b 1
)

echo Setting up frontend...
cd frontend
call npm ci --ignore-scripts
if errorlevel 1 (
    echo Error installing frontend dependencies.
    exit /b 1
)
cd ..

echo ========================================
echo Setup completed successfully!
echo Run 'runapplication.bat' to start both servers.
echo ========================================
