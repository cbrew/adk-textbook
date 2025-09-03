-- Migration 008 Step 1: Prepare for ADK compatibility
-- This step prepares the database for the main compatibility changes

-- Create backup tables first
CREATE TABLE sessions_backup AS SELECT * FROM sessions;
CREATE TABLE events_backup AS SELECT * FROM events;

-- Drop problematic indexes that prevent type conversions
DROP INDEX IF EXISTS idx_sessions_state_gin;
DROP INDEX IF EXISTS idx_events_data_gin;

-- Record this step
INSERT INTO schema_migrations (version, applied_at) VALUES ('008-step1', NOW());