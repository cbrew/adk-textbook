# ADK PostgreSQL Runtime Development Makefile

.PHONY: help setup dev-up dev-down migrate status test clean reset dev-setup

# Default target
help:
	@echo "ADK PostgreSQL Runtime Development Commands:"
	@echo ""
	@echo "  setup     - Install Python dependencies with uv"
	@echo "  dev-up    - Start development PostgreSQL containers"
	@echo "  dev-down  - Stop development containers"
	@echo "  migrate   - Run database migrations"
	@echo "  status    - Check database migration status"
	@echo "  test      - Run test suite"
	@echo "  clean     - Clean up development environment"
	@echo "  reset     - Reset database (WARNING: destroys all data)"
	@echo "  dev-setup - Complete setup: dependencies + containers + migrations"

# Install dependencies
setup:
	@echo "Installing dependencies with uv..."
	@command -v uv >/dev/null 2>&1 || (echo "ERROR: uv is not installed. Install it from https://docs.astral.sh/uv/" && exit 1)
	uv sync
	@echo "Dependencies installed successfully"

# Start development environment
dev-up:
	@echo "Checking if Docker is running..."
	@docker version > /dev/null 2>&1 || (echo "ERROR: Docker is not running. Please start Docker Desktop first." && exit 1)
	cd docker && docker compose up -d
	@echo "Waiting for PostgreSQL to start..."
	@sleep 10
	@echo "Development environment ready"
	@echo "PostgreSQL with pgvector: localhost:5432"
	@echo "Database: adk_runtime, User: adk_user"

# Stop development environment  
dev-down:
	cd docker && docker compose down
	@echo "Development environment stopped"

# Run database migrations
migrate: setup
	uv run python examples/setup_database.py
	@echo "Database migrations completed"

# Check migration status
status: setup
	uv run python scripts/check_migration_status.py

# Run tests
test: setup
	uv run pytest tests/ -v
	@echo "Tests completed"

# Clean development environment
clean: dev-down
	cd docker && docker compose down -v
	docker system prune -f
	@echo "Development environment cleaned"

# Reset database (development only!)
reset: setup
	uv run python scripts/reset_database.py

# Quick development setup
dev-setup: setup dev-up migrate
	@echo "Development environment ready!"
	@echo "Run 'make test' to verify everything works"