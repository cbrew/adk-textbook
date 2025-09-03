-- Migration 008 Step 3: Create ADK-compatible events table

-- Drop existing events table (we have backup)
DROP TABLE events;

-- Create new ADK-compatible events table
CREATE TABLE events (
    -- Primary key columns (composite key)
    id VARCHAR(128) NOT NULL,
    app_name VARCHAR(128) NOT NULL,
    user_id VARCHAR(128) NOT NULL,  
    session_id VARCHAR(128) NOT NULL,
    
    -- ADK-specific columns
    invocation_id VARCHAR(256) NOT NULL,
    author VARCHAR(256) NOT NULL,
    branch VARCHAR(256),
    timestamp TIMESTAMP NOT NULL,
    content TEXT,
    actions BYTEA NOT NULL DEFAULT ''::bytea,  -- Default empty bytea
    long_running_tool_ids_json TEXT,
    grounding_metadata TEXT,
    partial BOOLEAN,
    turn_complete BOOLEAN,
    error_code VARCHAR(256),
    error_message VARCHAR(1024),
    interrupted BOOLEAN,
    
    -- Constraints
    PRIMARY KEY (id, app_name, user_id, session_id),
    
    -- Foreign key to sessions table
    FOREIGN KEY (app_name, user_id, session_id) 
        REFERENCES sessions(app_name, user_id, id) 
        ON DELETE CASCADE
);

-- Add indexes for performance
CREATE INDEX idx_events_session ON events(app_name, user_id, session_id);
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_author ON events(author);

-- Record this step
INSERT INTO schema_migrations (version, applied_at) VALUES ('008-step3', NOW());