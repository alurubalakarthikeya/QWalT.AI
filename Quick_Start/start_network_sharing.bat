@echo off
setlocal enabledelayedexpansion
echo ================================================================
echo    KneadQuality-AI - Network Sharing Mode
echo ================================================================
echo.
echo This will make your AI available to anyone on your WiFi network
echo.

cd /d "%~dp0"

echo Finding your IP address...
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /i "IPv4"') do (
    set "ip=%%i"
    set "ip=!ip: =!"
    if defined ip (
        echo.
        echo ✅ Your IP Address: !ip!
        echo.
        echo 📡 Your AI will be available at: http://!ip!:8503
        echo.
        echo 📋 Share this URL with anyone on the same WiFi:
        echo    http://!ip!:8503
        echo.
        goto :found
    )
)

:found
echo ================================================================
echo Starting KneadQuality-AI with Network Access...
echo Press Ctrl+C to stop the server
echo ================================================================
echo.

streamlit run app_cloud.py --server.address 0.0.0.0 --server.port 8503

pause
