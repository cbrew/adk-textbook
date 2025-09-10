-- Migration 007: Convert UUID columns to VARCHAR for ADK compatibility
-- ADK's DatabaseSessionService expects string IDs, not UUIDs

-- Step 1: Drop foreign key constraints
ALTER TABLE events DROP CONSTRAINT IF EXISTS events_session_id_fkey;
ALTER TABLE memory DROP CONSTRAINT IF EXISTS memory_session_id_fkey;
ALTER TABLE artifacts DROP CONSTRAINT IF EXISTS artifacts_session_id_fkey;

-- Step 2: Convert all ID columns to VARCHAR
-- Convert sessions.id to VARCHAR
ALTER TABLE sessions ALTER COLUMN id TYPE VARCHAR(255);

-- Convert foreign key references in other tables
ALTER TABLE events ALTER COLUMN session_id TYPE VARCHAR(255);
ALTER TABLE memory ALTER COLUMN session_id TYPE VARCHAR(255);
ALTER TABLE artifacts ALTER COLUMN session_id TYPE VARCHAR(255);

-- Convert primary key columns to VARCHAR as well
ALTER TABLE events ALTER COLUMN id TYPE VARCHAR(255);
ALTER TABLE memory ALTER COLUMN id TYPE VARCHAR(255);  
ALTER TABLE artifacts ALTER COLUMN id TYPE VARCHAR(255);

-- Step 3: Recreate foreign key constraints
ALTER TABLE events ADD CONSTRAINT events_session_id_fkey 
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE;
    
ALTER TABLE memory ADD CONSTRAINT memory_session_id_fkey 
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE;
    
ALTER TABLE artifacts ADD CONSTRAINT artifacts_session_id_fkey 
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE;

-- Add comments for clarity
COMMENT ON COLUMN sessions.id IS 'Session ID - VARCHAR for ADK DatabaseSessionService compatibility';
COMMENT ON COLUMN events.id IS 'Event ID - VARCHAR for consistency';
COMMENT ON COLUMN memory.id IS 'Memory ID - VARCHAR for consistency';
COMMENT ON COLUMN artifacts.id IS 'Artifact ID - VARCHAR for consistency';