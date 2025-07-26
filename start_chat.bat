@echo off
echo.
echo =========================================
echo   🚀 KneadQuality-AI Chat Launcher 🚀
echo =========================================
echo.
echo Starting the enhanced chat interface...
echo.

cd /d "c:\Users\AYUSH SINGH\Documents\GitHub\KneadQuality-AI\Core_Applications"

echo 📊 Launching KneadQuality-AI Chat...
echo 💬 Chat interface will open in your browser
echo 🌐 Local URL: http://localhost:8510
echo 🔗 Network URL: http://192.168.29.51:8510
echo.
echo ⚡ Features available:
echo   • Smart conversational AI
echo   • Quality management expertise
echo   • Process improvement guidance
echo   • Document search capabilities
echo   • Interactive chat interface
echo.

streamlit run chat_app.py --server.port 8510

pause
