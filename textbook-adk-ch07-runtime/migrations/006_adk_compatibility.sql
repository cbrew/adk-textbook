-- Migration 006: ADK Built-in Service Compatibility
-- Makes our PostgreSQL schema compatible with ADK's DatabaseSessionService

-- Add app_name column to sessions table
ALTER TABLE sessions ADD COLUMN app_name VARCHAR(255);

-- Set default app_name for existing sessions
UPDATE sessions SET app_name = 'postgres_chat_agent' WHERE app_name IS NULL;

-- Make app_name NOT NULL and add default
ALTER TABLE sessions ALTER COLUMN app_name SET NOT NULL;
ALTER TABLE sessions ALTER COLUMN app_name SET DEFAULT 'postgres_chat_agent';

-- Rename timestamp columns to match ADK expectations
ALTER TABLE sessions RENAME COLUMN created_at TO create_time;
ALTER TABLE sessions RENAME COLUMN updated_at TO update_time;

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_sessions_app_name ON sessions(app_name);
CREATE INDEX IF NOT EXISTS idx_sessions_app_user ON sessions(app_name, user_id);

-- Add comments for clarity
COMMENT ON COLUMN sessions.app_name IS 'Application name - required by ADK DatabaseSessionService';
COMMENT ON COLUMN sessions.create_time IS 'Session creation time - renamed for ADK compatibility';
COMMENT ON COLUMN sessions.update_time IS 'Session update time - renamed for ADK compatibility';