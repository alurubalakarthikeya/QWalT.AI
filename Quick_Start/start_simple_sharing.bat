@echo off
echo ================================================================
echo    KneadQuality-AI - Simple Network Sharing
echo ================================================================
echo.
echo Finding your network IP address...
echo.

ipconfig | findstr /i "IPv4"

echo.
echo ================================================================
echo Your AI will be available at one of these addresses:
echo Look for your main network adapter above
echo Example: http://192.168.1.100:8503
echo ================================================================
echo.
echo Starting KneadQuality-AI for network access...
echo Share the URL with anyone on your WiFi network!
echo Press Ctrl+C to stop
echo.

cd /d "%~dp0"
streamlit run app_cloud.py --server.address 0.0.0.0 --server.port 8503

pause
