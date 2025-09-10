-- Migration 008 Step 4: Migrate existing event data to new ADK structure

-- Insert our existing event data into the new structure
INSERT INTO events (
    id, 
    app_name, 
    user_id,
    session_id,
    invocation_id,
    author,
    branch,
    timestamp,
    content,
    actions,
    long_running_tool_ids_json,
    grounding_metadata,
    partial,
    turn_complete,
    error_code,
    error_message,
    interrupted
)
SELECT 
    e.id,
    s.app_name,
    s.user_id,
    e.session_id,
    -- Map our event_type to invocation_id
    COALESCE(e.event_type, 'unknown_invocation') as invocation_id,
    -- Extract author from event_data or default based on event_type
    COALESCE(
        e.event_data->>'author',
        CASE 
            WHEN e.event_type = 'user_message' THEN 'user'
            WHEN e.event_type = 'assistant_message' THEN 'assistant'
            ELSE 'system'
        END
    ) as author,
    -- Extract branch or set to NULL
    e.event_data->>'branch' as branch,
    e.timestamp,
    -- Extract content from event_data
    COALESCE(
        e.event_data->>'content',
        e.event_data->>'message',
        e.event_data::TEXT
    ) as content,
    -- Convert event_data to bytea for actions column (simple approach)
    e.event_data::TEXT::bytea as actions,
    -- Extract tool IDs if available
    e.event_data->>'tool_ids' as long_running_tool_ids_json,
    -- Grounding metadata
    e.event_data->>'grounding_metadata' as grounding_metadata,
    -- Boolean flags
    (e.event_data->>'partial')::BOOLEAN as partial,
    COALESCE((e.event_data->>'turn_complete')::BOOLEAN, true) as turn_complete,
    -- Error information  
    e.event_data->>'error_code' as error_code,
    e.event_data->>'error_message' as error_message,
    (e.event_data->>'interrupted')::BOOLEAN as interrupted
FROM events_backup e
JOIN sessions s ON e.session_id = s.id;

-- Record this step
INSERT INTO schema_migrations (version, applied_at) VALUES ('008-step4', NOW());