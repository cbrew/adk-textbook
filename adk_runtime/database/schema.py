"""
Database schema definitions for ADK runtime.

Simple, transparent SQL schema optimized for ADK's event-driven architecture.
"""

# Current schema version for migration management
SCHEMA_VERSION = "002"

# Core table creation SQL - simple and efficient
SCHEMA_SQL = {
    "001_create_sessions": """
        CREATE TABLE IF NOT EXISTS sessions (
            id UUID PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            state JSONB NOT NULL DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
        CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at);
        CREATE INDEX IF NOT EXISTS idx_sessions_state_gin ON sessions USING GIN(state);
    """,
    
    "002_create_events": """
        CREATE TABLE IF NOT EXISTS events (
            id UUID PRIMARY KEY,
            session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
            event_type VARCHAR(100) NOT NULL,
            event_data JSONB NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_events_session_id ON events(session_id);
        CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
        CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
        CREATE INDEX IF NOT EXISTS idx_events_data_gin ON events USING GIN(event_data);
    """,
    
    "003_create_artifacts": """
        CREATE TABLE IF NOT EXISTS artifacts (
            id UUID PRIMARY KEY,
            session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
            filename VARCHAR(500) NOT NULL,
            content_type VARCHAR(100),
            file_size BIGINT,
            file_path TEXT NOT NULL,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX IF NOT EXISTS idx_artifacts_session_id ON artifacts(session_id);
        CREATE INDEX IF NOT EXISTS idx_artifacts_filename ON artifacts(filename);
        CREATE INDEX IF NOT EXISTS idx_artifacts_created_at ON artifacts(created_at);
    """,
    
    "004_create_memory": """
        CREATE TABLE IF NOT EXISTS memory (
            id UUID PRIMARY KEY,
            session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
            user_id VARCHAR(255),
            content TEXT NOT NULL,
            embedding VECTOR(384),
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            CONSTRAINT memory_scope_check CHECK (
                (session_id IS NOT NULL AND user_id IS NULL) OR 
                (session_id IS NULL AND user_id IS NOT NULL)
            )
        );
        
        CREATE INDEX IF NOT EXISTS idx_memory_session_id ON memory(session_id);
        CREATE INDEX IF NOT EXISTS idx_memory_user_id ON memory(user_id);
        CREATE INDEX IF NOT EXISTS idx_memory_created_at ON memory(created_at);
        CREATE INDEX IF NOT EXISTS idx_memory_metadata_gin ON memory USING GIN(metadata);
        CREATE INDEX IF NOT EXISTS idx_memory_embedding ON memory USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
    """,
    
    "005_create_migrations": """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(10) PRIMARY KEY,
            applied_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """,
    
    "006_enhance_artifacts_postgresql_storage": """
        -- Add BYTEA storage column for PostgreSQL artifact storage
        ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS file_data BYTEA;
        
        -- Add event reference for event sourcing integration
        ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS event_id UUID REFERENCES events(id) ON DELETE SET NULL;
        
        -- Add storage type indicator (postgresql/filesystem)
        ALTER TABLE artifacts ADD COLUMN IF NOT EXISTS storage_type VARCHAR(20) DEFAULT 'filesystem';
        
        -- Add indexes for the new columns
        CREATE INDEX IF NOT EXISTS idx_artifacts_event_id ON artifacts(event_id);
        CREATE INDEX IF NOT EXISTS idx_artifacts_storage_type ON artifacts(storage_type);
    """,
    
}

# Optimized queries for common operations
QUERIES = {
    # Session operations
    "insert_session": """
        INSERT INTO sessions (id, user_id, state) 
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET 
            state = EXCLUDED.state,
            updated_at = NOW()
    """,
    
    "get_session": """
        SELECT id, user_id, state, created_at, updated_at 
        FROM sessions 
        WHERE id = %s
    """,
    
    "update_session_state": """
        UPDATE sessions 
        SET state = %s, updated_at = NOW() 
        WHERE id = %s
    """,
    
    "get_user_sessions": """
        SELECT id, user_id, state, created_at, updated_at 
        FROM sessions 
        WHERE user_id = %s 
        ORDER BY updated_at DESC 
        LIMIT %s
    """,
    
    # Event operations
    "insert_event": """
        INSERT INTO events (id, session_id, event_type, event_data) 
        VALUES (%s, %s, %s, %s)
    """,
    
    "get_session_events": """
        SELECT id, session_id, event_type, event_data, timestamp 
        FROM events 
        WHERE session_id = %s 
        ORDER BY timestamp ASC
    """,
    
    "get_recent_events": """
        SELECT id, session_id, event_type, event_data, timestamp 
        FROM events 
        WHERE session_id = %s 
        ORDER BY timestamp DESC 
        LIMIT %s
    """,
    
    # Artifact operations
    "insert_artifact": """
        INSERT INTO artifacts (id, session_id, filename, content_type, file_size, file_path, metadata, file_data, event_id, storage_type) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """,
    
    "get_artifact": """
        SELECT id, session_id, filename, content_type, file_size, file_path, metadata, created_at, file_data, event_id, storage_type 
        FROM artifacts 
        WHERE id = %s
    """,
    
    "get_session_artifacts": """
        SELECT id, session_id, filename, content_type, file_size, file_path, metadata, created_at, file_data, event_id, storage_type 
        FROM artifacts 
        WHERE session_id = %s 
        ORDER BY created_at DESC
    """,
    
    "get_artifact_by_filename": """
        SELECT id, session_id, filename, content_type, file_size, file_path, metadata, created_at, file_data, event_id, storage_type 
        FROM artifacts 
        WHERE session_id = %s AND filename = %s
        ORDER BY created_at DESC
    """,
    
    # Memory operations
    "insert_memory": """
        INSERT INTO memory (id, session_id, user_id, content, embedding, metadata) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """,
    
    "get_session_memory": """
        SELECT id, session_id, user_id, content, embedding, metadata, created_at 
        FROM memory 
        WHERE session_id = %s 
        ORDER BY created_at DESC
    """,
    
    "get_user_memory": """
        SELECT id, session_id, user_id, content, embedding, metadata, created_at 
        FROM memory 
        WHERE user_id = %s 
        ORDER BY created_at DESC 
        LIMIT %s
    """,
    
    "search_memory": """
        SELECT id, session_id, user_id, content, embedding, metadata, created_at 
        FROM memory 
        WHERE content ILIKE %s 
        AND (session_id = %s OR user_id = %s)
        ORDER BY created_at DESC 
        LIMIT %s
    """,
    
    "search_memory_by_embedding": """
        SELECT id, session_id, user_id, content, embedding, metadata, created_at,
               (embedding <=> %s) AS distance
        FROM memory 
        WHERE (session_id = %s OR user_id = %s)
        ORDER BY embedding <=> %s 
        LIMIT %s
    """,
}


def get_schema_sql(version: str) -> str:
    """Get SQL for a specific schema version."""
    key = f"{version:03d}_" if version.isdigit() else version
    for schema_key in SCHEMA_SQL:
        if schema_key.startswith(key):
            return SCHEMA_SQL[schema_key]
    raise ValueError(f"Schema version {version} not found")


def get_all_schema_versions() -> list[str]:
    """Get all available schema versions in order."""
    versions = []
    for key in SCHEMA_SQL:
        if key.startswith(('001_', '002_', '003_', '004_', '005_', '006_')):
            versions.append(key.split('_')[0])
    return sorted(set(versions))