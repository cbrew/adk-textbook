# ADK PostgreSQL Runtime Development Makefile

.PHONY: help setup podman-setup dev-up dev-down migrate status test clean reset dev-setup

# Default target
help:
	@echo "ADK PostgreSQL Runtime Development Commands:"
	@echo ""
	@echo "  setup        - Install Python dependencies with uv"
	@echo "  podman-setup - Initialize and start Podman machine (Mac only)"
	@echo "  dev-up       - Start development PostgreSQL containers"
	@echo "  dev-down     - Stop development containers"
	@echo "  migrate      - Run database migrations"
	@echo "  status       - Check database migration status"
	@echo "  test         - Run test suite"
	@echo "  clean        - Clean up development environment"
	@echo "  reset        - Reset database (WARNING: destroys all data)"
	@echo "  dev-setup    - Complete setup: dependencies + containers + migrations"

# Install dependencies
setup:
	@echo "Installing dependencies with uv..."
	@command -v uv >/dev/null 2>&1 || (echo "ERROR: uv is not installed. Install it from https://docs.astral.sh/uv/" && exit 1)
	uv sync
	@echo "Dependencies installed successfully"

# Initialize Podman machine (Mac only)
podman-setup:
	@echo "Setting up Podman machine..."
	@command -v podman > /dev/null 2>&1 || (echo "ERROR: Podman is not installed. Install with: brew install podman" && exit 1)
	@echo "Installing podman-compose..."
	@pip install podman-compose > /dev/null 2>&1 || echo "podman-compose already installed or pip not available"
	@echo "Creating Podman auth configuration..."
	@mkdir -p ~/.config/containers
	@echo '{"auths": {}}' > ~/.config/containers/auth.json
	@if [ "$$(uname)" = "Darwin" ]; then \
		echo "Initializing Podman machine (Mac)..."; \
		podman machine init --now 2>/dev/null || podman machine start || echo "Podman machine already running"; \
	else \
		echo "Podman machine setup not needed on Linux"; \
	fi
	@podman version > /dev/null 2>&1 && echo "Podman is ready!" || echo "WARNING: Podman may not be ready"

# Start development environment
dev-up:
	@echo "Checking if Podman is available..."
	@command -v podman > /dev/null 2>&1 || (echo "ERROR: Podman is not installed. Install with: brew install podman" && exit 1)
	@podman version > /dev/null 2>&1 || (echo "ERROR: Podman is not running. Start with: podman machine start" && exit 1)
	@echo "Ensuring Podman auth configuration..."
	@mkdir -p ~/.config/containers
	@test -f ~/.config/containers/auth.json || echo '{"auths": {}}' > ~/.config/containers/auth.json
	@echo "Creating persistent data directories..."
	@mkdir -p docker/data/postgres docker/data/postgres-vector
	@echo "Using Podman..."
	cd docker && (command -v podman-compose > /dev/null 2>&1 && podman-compose up -d || DOCKER_COMPOSE_PROVIDER="" podman compose up -d)
	@echo "Waiting for PostgreSQL instances to start..."
	@sleep 10
	@echo "Development environment ready"
	@echo "Main PostgreSQL with pgvector: localhost:5432"
	@echo "Vector PostgreSQL with pgvector: localhost:5433"
	@echo "Database: adk_runtime, User: adk_user"
	@echo "Data persisted to: docker/data/postgres/ and docker/data/postgres-vector/"

# Stop development environment  
dev-down:
	cd docker && (command -v podman-compose > /dev/null 2>&1 && podman-compose down || DOCKER_COMPOSE_PROVIDER="" podman compose down)
	@echo "Development environment stopped"

# Run database migrations
migrate: setup
	cd .. && uv run python textbook-adk-ch07-runtime/examples/setup_database.py
	@echo "Database migrations completed"

# Check migration status
status: setup
	cd .. && uv run python textbook-adk-ch07-runtime/scripts/check_migration_status.py

# Run tests
test: setup
	cd .. && uv run pytest textbook-adk-ch07-runtime/tests/ -v
	@echo "Tests completed"

# Clean development environment
clean: dev-down
	cd docker && (command -v podman-compose > /dev/null 2>&1 && podman-compose down -v || DOCKER_COMPOSE_PROVIDER="" podman compose down -v)
	podman system prune -f
	@echo "Development environment cleaned"

# Reset database (development only!)
reset: setup
	cd .. && uv run python textbook-adk-ch07-runtime/scripts/reset_database.py

# Quick development setup
dev-setup: setup dev-up migrate
	@echo "Development environment ready!"
	@echo "Run 'make test' to verify everything works"