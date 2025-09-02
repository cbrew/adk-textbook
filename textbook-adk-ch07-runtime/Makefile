# ADK PostgreSQL Runtime Development Makefile

.PHONY: help setup dev-up dev-down migrate status test clean reset

# Default target
help:
	@echo "ADK PostgreSQL Runtime Development Commands:"
	@echo ""
	@echo "  setup     - Install Python dependencies"
	@echo "  dev-up    - Start development PostgreSQL containers"
	@echo "  dev-down  - Stop development containers"
	@echo "  migrate   - Run database migrations"
	@echo "  status    - Check database migration status"
	@echo "  test      - Run test suite"
	@echo "  clean     - Clean up development environment"
	@echo "  reset     - Reset database (WARNING: destroys all data)"

# Install dependencies
setup:
	pip install -r requirements.txt
	@echo "Dependencies installed"

# Start development environment
dev-up:
	@echo "Checking if Docker is running..."
	@docker version > /dev/null 2>&1 || (echo "ERROR: Docker is not running. Please start Docker Desktop first." && exit 1)
	docker-compose -f docker/docker-compose.yml up -d
	@echo "Waiting for PostgreSQL to start..."
	@sleep 10
	@echo "Development environment ready"
	@echo "Standard PostgreSQL: localhost:5432"
	@echo "Vector PostgreSQL:   localhost:5433"

# Stop development environment  
dev-down:
	docker-compose -f docker/docker-compose.yml down
	@echo "Development environment stopped"

# Run database migrations
migrate: setup
	python examples/setup_database.py
	@echo "Database migrations completed"

# Check migration status
status: setup
	python scripts/check_migration_status.py

# Run tests
test: setup
	python -m pytest tests/ -v
	@echo "Tests completed"

# Clean development environment
clean: dev-down
	docker-compose -f docker/docker-compose.yml down -v
	docker system prune -f
	@echo "Development environment cleaned"

# Reset database (development only!)
reset: setup
	python scripts/reset_database.py

# Quick development setup
dev-setup: setup dev-up migrate
	@echo "Development environment ready!"
	@echo "Run 'make test' to verify everything works"