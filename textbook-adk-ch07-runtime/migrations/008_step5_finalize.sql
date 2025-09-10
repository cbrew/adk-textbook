-- Migration 008 Step 5: Finalize ADK compatibility

-- Ensure app_states table matches ADK expectations
ALTER TABLE app_states ALTER COLUMN app_name TYPE VARCHAR(128);
ALTER TABLE app_states ALTER COLUMN state TYPE TEXT USING state::TEXT;
ALTER TABLE app_states ALTER COLUMN update_time TYPE TIMESTAMP USING update_time;

-- Ensure user_states table matches ADK expectations  
ALTER TABLE user_states ALTER COLUMN app_name TYPE VARCHAR(128);
ALTER TABLE user_states ALTER COLUMN user_id TYPE VARCHAR(128);
ALTER TABLE user_states ALTER COLUMN state TYPE TEXT USING state::TEXT;
ALTER TABLE user_states ALTER COLUMN update_time TYPE TIMESTAMP USING update_time;

-- Add helpful comments
COMMENT ON TABLE sessions IS 'Sessions table - fully compatible with ADK DatabaseSessionService composite key (app_name, user_id, id)';
COMMENT ON TABLE events IS 'Events table - fully restructured to match ADK DatabaseSessionService schema';
COMMENT ON TABLE app_states IS 'Application states - compatible with ADK DatabaseSessionService';
COMMENT ON TABLE user_states IS 'User states - compatible with ADK DatabaseSessionService';
COMMENT ON TABLE sessions_backup IS 'Backup of original sessions table before ADK compatibility migration';
COMMENT ON TABLE events_backup IS 'Backup of original events table before ADK compatibility migration';

-- Record this final step
INSERT INTO schema_migrations (version, applied_at) VALUES ('008-step5', NOW());
INSERT INTO schema_migrations (version, applied_at) VALUES ('008', NOW());