-- Migration 009: Fix state column types for ADK's DynamicJSON compatibility
-- 
-- ADK uses a custom DynamicJSON type that expects JSON-compatible columns,
-- not plain TEXT. PostgreSQL's JSONB is compatible with this.

-- Convert state columns back to JSONB (which works with ADK's DynamicJSON)
ALTER TABLE sessions ALTER COLUMN state TYPE JSONB USING state::JSONB;
ALTER TABLE app_states ALTER COLUMN state TYPE JSONB USING state::JSONB;  
ALTER TABLE user_states ALTER COLUMN state TYPE JSONB USING state::JSONB;

-- Add helpful comments about the types
COMMENT ON COLUMN sessions.state IS 'JSONB state - compatible with ADK DynamicJSON type';
COMMENT ON COLUMN app_states.state IS 'JSONB state - compatible with ADK DynamicJSON type';
COMMENT ON COLUMN user_states.state IS 'JSONB state - compatible with ADK DynamicJSON type';

-- Record this fix
INSERT INTO schema_migrations (version, applied_at) VALUES ('009', NOW());