-- Initialize ADK runtime database with pgvector extension
-- This script runs when the pgvector-enabled PostgreSQL container starts

-- Create user if not exists (for development)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'adk_user') THEN
        CREATE USER adk_user WITH PASSWORD 'adk_password';
    END IF;
END
$$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE adk_runtime TO adk_user;
GRANT ALL ON SCHEMA public TO adk_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO adk_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO adk_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO adk_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO adk_user;

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Basic configuration for development
SET timezone = 'UTC';

-- Note: The actual tables with vector columns will be created by the migration system
-- This just sets up the database, user permissions, and vector extension