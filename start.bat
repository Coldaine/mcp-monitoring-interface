@echo off
REM MCP Monitoring Interface - Windows Startup Script

echo ============================================================
echo MCP Monitoring Interface
echo ============================================================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo [WARNING] No virtual environment found. Using global Python.
)

echo.
echo [INFO] Running component tests...
python test_app.py
if errorlevel 1 (
    echo.
    echo [ERROR] Component tests failed. Please check the output above.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Starting Gradio Interface...
echo ============================================================
echo.
echo The dashboard will be available at: http://localhost:7860
echo.
echo Press Ctrl+C to stop the server.
echo.

python gradio_app.py

pause
