#!/bin/bash
"""
Launch ADK Web UI with PostgreSQL runtime services.

This script starts the ADK web UI plugin system wired with our PostgreSQL-based
session, memory, and artifact services from Chapter 7's runtime implementation.

Prerequisites:
- PostgreSQL services running (make dev-up)
- Database migrations applied (make migrate)
- Environment variables loaded from .env

Usage:
    ./run_postgres_web_ui.sh [agent_directory] [additional_adk-webx_options...]

Examples:
    ./run_postgres_web_ui.sh postgres_chat_agent
    ./run_postgres_web_ui.sh postgres_chat_agent --port 8080
    ./run_postgres_web_ui.sh postgres_chat_agent --host 0.0.0.0 --port 8080
"""

set -e

# Default values
DEFAULT_AGENT_DIR="postgres_chat_agent"
DEFAULT_HOST="127.0.0.1"
DEFAULT_PORT="8000"

# Get agent directory from first argument or use default
AGENT_DIR="${1:-$DEFAULT_AGENT_DIR}"

# Remove first argument if it was provided, leaving remaining args for adk-webx
if [ $# -gt 0 ]; then
    shift
fi

# Check if agent directory exists
if [ ! -d "$AGENT_DIR" ]; then
    echo "❌ Agent directory '$AGENT_DIR' not found!"
    echo "Available agents:"
    find . -maxdepth 2 -name "*.yaml" -o -name "agent.py" | grep -v __pycache__ | head -5
    exit 1
fi

# Check if PostgreSQL is running
echo "🔍 Checking PostgreSQL services..."
if ! pg_isready -h localhost -p 5432 -U adk_user >/dev/null 2>&1; then
    echo "❌ PostgreSQL not ready on port 5432!"
    echo "Please start services with: make dev-up"
    exit 1
fi

if ! pg_isready -h localhost -p 5433 -U adk_user >/dev/null 2>&1; then
    echo "❌ PostgreSQL vector DB not ready on port 5433!" 
    echo "Please start services with: make dev-up"
    exit 1
fi

echo "✅ PostgreSQL services are running"

# Load environment variables
if [ -f ".env" ]; then
    echo "📝 Loading environment from .env"
    export $(grep -v '^#' .env | xargs)
else
    echo "⚠️  No .env file found - using defaults"
fi

# Check if adk_web_ui plugin package is available
cd adk_web_ui
if [ ! -f "pyproject.toml" ]; then
    echo "❌ ADK web UI plugin system not found!"
    echo "Please ensure adk_web_ui/ directory contains the plugin system"
    exit 1
fi

# Install the plugin system in development mode if needed
echo "🔧 Installing adk-service-plugins in development mode..."
pip install -e . >/dev/null 2>&1 || {
    echo "❌ Failed to install adk-service-plugins"
    exit 1
}

cd ..

echo ""
echo "🚀 Starting ADK Web UI with PostgreSQL Runtime Services"
echo "   Agent Directory: $AGENT_DIR"
echo "   Plugin System: adk-service-plugins"
echo "   Runtime: PostgreSQL-backed services"
echo ""

# Launch the web UI with PostgreSQL services
exec adk-webx \
    --agent-dir "$AGENT_DIR" \
    --session-service "postgres-runtime:" \
    --memory-service "postgres-runtime:" \
    --artifact-service "postgres-runtime:" \
    --plugin python:examples.postgres_runtime_plugin \
    "$@"