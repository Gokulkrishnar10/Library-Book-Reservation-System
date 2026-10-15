@echo off
cd /d "%~dp0"

echo ===================================================
echo   Starting Library Reservation System (v2.1)
echo ===================================================
echo [1/2] Starting FastAPI Backend on http://localhost:8000 ...
start "Library Backend (Port 8000)" cmd /k "title Library Backend (Port 8000) && cd /d "%~dp0" && call env\Scripts\activate && python main.py"

echo [2/2] Starting Vite Frontend on http://localhost:5173 ...
cd /d "%~dp0frontend"
call npm start

