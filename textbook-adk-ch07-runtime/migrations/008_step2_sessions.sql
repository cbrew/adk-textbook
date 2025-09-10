-- Migration 008 Step 2: Update sessions table for ADK compatibility

-- Drop foreign key constraints that reference sessions
ALTER TABLE events DROP CONSTRAINT IF EXISTS events_session_id_fkey;
ALTER TABLE memory DROP CONSTRAINT IF EXISTS memory_session_id_fkey;
ALTER TABLE artifacts DROP CONSTRAINT IF EXISTS artifacts_session_id_fkey;

-- Drop existing primary key constraint
ALTER TABLE sessions DROP CONSTRAINT sessions_pkey;

-- Ensure all sessions have unique (app_name, user_id, id) combinations
DO $$
DECLARE
    rec RECORD;
    counter INT;
BEGIN
    FOR rec IN 
        SELECT app_name, user_id, id, COUNT(*) as cnt
        FROM sessions 
        GROUP BY app_name, user_id, id 
        HAVING COUNT(*) > 1
    LOOP
        counter := 1;
        UPDATE sessions 
        SET id = id || '-dup-' || counter
        WHERE ctid NOT IN (
            SELECT ctid FROM sessions 
            WHERE app_name = rec.app_name AND user_id = rec.user_id AND id = rec.id 
            LIMIT 1
        )
        AND app_name = rec.app_name AND user_id = rec.user_id AND id = rec.id;
        counter := counter + 1;
    END LOOP;
END $$;

-- Add the composite primary key constraint
ALTER TABLE sessions ADD CONSTRAINT sessions_pkey PRIMARY KEY (app_name, user_id, id);

-- Update column types to match ADK expectations
ALTER TABLE sessions ALTER COLUMN app_name TYPE VARCHAR(128);
ALTER TABLE sessions ALTER COLUMN user_id TYPE VARCHAR(128);  
ALTER TABLE sessions ALTER COLUMN id TYPE VARCHAR(128);

-- Convert JSONB state to TEXT
ALTER TABLE sessions ALTER COLUMN state TYPE TEXT USING state::TEXT;

-- Ensure create_time and update_time are proper DATETIME
ALTER TABLE sessions ALTER COLUMN create_time TYPE TIMESTAMP USING create_time;
ALTER TABLE sessions ALTER COLUMN update_time TYPE TIMESTAMP USING update_time;

-- Ensure NOT NULL constraints
ALTER TABLE sessions ALTER COLUMN create_time SET NOT NULL;
ALTER TABLE sessions ALTER COLUMN update_time SET NOT NULL;

-- Record this step
INSERT INTO schema_migrations (version, applied_at) VALUES ('008-step2', NOW());