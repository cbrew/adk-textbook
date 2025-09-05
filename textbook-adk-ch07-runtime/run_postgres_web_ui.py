#!/usr/bin/env python3
"""
Launch ADK Web UI with PostgreSQL runtime services.

This script starts the ADK web UI plugin system wired with our PostgreSQL-based
session, memory, and artifact services from Chapter 7's runtime implementation.

Prerequisites:
- PostgreSQL services running (make dev-up)
- Database migrations applied (make migrate)
- Environment variables loaded from .env

Usage:
    python run_postgres_web_ui.py [agent_directory] [--host HOST] [--port PORT]

Examples:
    python run_postgres_web_ui.py postgres_chat_agent
    python run_postgres_web_ui.py postgres_chat_agent --port 8080
    python run_postgres_web_ui.py postgres_chat_agent --host 0.0.0.0 --port 8080
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

import psycopg2


def check_postgres_connection(host: str, port: int, user: str, database: str) -> bool:
    """Check if PostgreSQL is accessible."""
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            database=database,
            connect_timeout=3
        )
        conn.close()
        return True
    except (psycopg2.Error, Exception):
        return False


def load_env_file(env_path: str = ".env"):
    """Load environment variables from .env file."""
    if not os.path.exists(env_path):
        print(f"⚠️  No {env_path} file found - using defaults")
        return

    print(f"📝 Loading environment from {env_path}")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value


def find_agents() -> list[str]:
    """Find available agent directories."""
    agents = []
    for path in Path('.').iterdir():
        if path.is_dir() and not path.name.startswith('.'):
            if (path / 'agent.py').exists() or list(path.glob('*.yaml')):
                agents.append(path.name)
    return agents


def main():
    parser = argparse.ArgumentParser(
        description='Launch ADK Web UI with PostgreSQL services'
    )
    parser.add_argument('agent_dir', nargs='?', default='postgres_chat_agent',
                       help='Agent directory (default: postgres_chat_agent)')
    parser.add_argument('--host', default='127.0.0.1',
                       help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000,
                       help='Port to bind to (default: 8000)')

    args = parser.parse_args()

    # Check if agent directory exists
    agent_path = Path(args.agent_dir)
    if not agent_path.exists():
        print(f"❌ Agent directory '{args.agent_dir}' not found!")
        agents = find_agents()
        if agents:
            print("Available agents:")
            for agent in agents[:5]:  # Show first 5
                print(f"  - {agent}")
        sys.exit(1)

    # Load environment variables
    load_env_file()

    # Check PostgreSQL connections
    print("🔍 Checking PostgreSQL services...")

    if not check_postgres_connection('localhost', 5432, 'adk_user', 'adk_runtime'):
        print("❌ PostgreSQL not ready on port 5432!")
        print("Please start services with: make dev-up")
        sys.exit(1)

    if not check_postgres_connection('localhost', 5433, 'adk_user', 'adk_runtime'):
        print("❌ PostgreSQL vector DB not ready on port 5433!")
        print("Please start services with: make dev-up")
        sys.exit(1)

    print("✅ PostgreSQL services are running")

    # Check if adk_web_ui plugin package is available
    adk_web_ui_path = Path('adk_web_ui')
    pyproject_path = adk_web_ui_path / 'pyproject.toml'
    if not adk_web_ui_path.exists() or not pyproject_path.exists():
        print("❌ ADK web UI plugin system not found!")
        print("Please ensure adk_web_ui/ directory contains the plugin system")
        sys.exit(1)

    # Install the plugin system in development mode if needed
    print("🔧 Installing adk-service-plugins in development mode...")
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-e', str(adk_web_ui_path)],
            check=True,
            capture_output=True
        )
    except subprocess.CalledProcessError:
        print("❌ Failed to install adk-service-plugins")
        sys.exit(1)

    print()
    print("🚀 Starting ADK Web UI with PostgreSQL Runtime Services")
    print(f"   Agent Directory: {args.agent_dir}")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print("   Plugin System: adk-service-plugins")
    print("   Runtime: PostgreSQL-backed services")
    print()

    # Build command
    cmd = [
        'adk-webx',
        '--agent-dir', args.agent_dir,
        '--host', args.host,
        '--port', str(args.port),
        '--session-service', 'postgres-runtime:',
        '--memory-service', 'postgres-runtime:',
        '--artifact-service', 'postgres-runtime:',
        '--plugin', 'python:examples.postgres_runtime_plugin'
    ]

    # Execute the command
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start web UI: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Web UI stopped")


if __name__ == '__main__':
    main()

