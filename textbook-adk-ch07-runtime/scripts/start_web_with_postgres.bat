@echo off
REM Start ADK web server with PostgreSQL session service integration
REM This script demonstrates partial integration with ADK's built-in services

setlocal enabledelayedexpansion

REM Configuration
set DATABASE_URL=postgresql://adk_user:adk_password@localhost:5432/adk_runtime
set PORT=8000

echo 🚀 Starting ADK Web Server with PostgreSQL Integration
echo.

echo 📋 Checking prerequisites...
pg_isready -h localhost -p 5432 -U adk_user -d adk_runtime >nul 2>&1
if errorlevel 1 (
    echo ❌ PostgreSQL is not running or not accessible
    echo 💡 Run 'make dev-up' to start PostgreSQL services
    exit /b 1
)
echo ✅ PostgreSQL is running

echo.
echo 🔧 ADK Web Integration Status:
echo   ✅ Session Service: PostgreSQL (--session_service_uri^)
echo   ⚠️  Memory Service: Custom PostgreSQL (not integrated with web UI^)
echo   ⚠️  Artifact Service: Custom PostgreSQL (not integrated with web UI^)

echo.
echo 📝 Note:
echo   • Session state from agent tools will be visible in the web UI
echo   • Memory and artifact operations will use our custom services
echo   • This provides partial integration - sessions work, but memory/artifacts don't appear in UI

echo.
echo 🌐 Starting ADK web server...
echo    URL: http://127.0.0.1:%PORT%
echo    Agent: postgres_chat_agent
echo.

REM Start the ADK web server with PostgreSQL session service
uv run adk web postgres_chat_agent --session_service_uri "%DATABASE_URL%" --port %PORT% --host "127.0.0.1"