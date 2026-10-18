@echo off
chcp 65001 >nul
rem ============================================================
rem  Jiangsu Lishui Senior High School - Archive Restore Site
rem  Double-click to start local preview server
rem ============================================================
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3 first.
    echo         https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Starting local preview server...
echo   URL: http://127.0.0.1:8897/index.html
echo.
echo   Press Ctrl+C to stop.
echo   Do NOT close this window while browsing.
echo ============================================
echo.

start "" http://127.0.0.1:8897/index.html
python -m http.server 8897
pause
