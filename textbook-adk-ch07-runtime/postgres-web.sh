#!/bin/bash
#
# Convenience wrapper for adk-postgres-web with PostgreSQL services
#
# Usage:
#   ./postgres-web.sh [PORT]
#
# Examples:
#   ./postgres-web.sh          # Uses default port 8000
#   ./postgres-web.sh 8080     # Uses port 8080
#

# Default port
PORT=${1:-8000}

echo "🚀 Starting ADK Web UI with PostgreSQL Services"
echo "   Port: $PORT"
echo "   Services: All PostgreSQL-backed (session, memory, artifact)"
echo

# Run the command with full PostgreSQL services integration
uv run adk-postgres-web \
  --session_service_uri "python:adk_postgres_web.postgres_services:create_session_service" \
  --memory_service_uri "python:adk_postgres_web.postgres_services:create_memory_service" \
  --artifact_service_uri "python:adk_postgres_web.postgres_services:create_artifact_service" \
  --host 127.0.0.1 \
  --port $PORT