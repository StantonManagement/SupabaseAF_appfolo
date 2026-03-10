-- Initialize Sync State for All Endpoints
-- Run this in Supabase SQL Editor to fix "Endpoint not found" errors

-- =============================================================================
-- Initialize sync state entries for all 4 datasets
-- =============================================================================

-- This will create initial entries in appfolio_sync_state table
-- The update_sync_state function requires these entries to exist

INSERT INTO appfolio_sync_state (endpoint, sync_method, last_synced_at, last_run_status, last_row_count)
VALUES
    ('work_order', 'delta', '1970-01-01T00:00:00Z', 'success', 0),
    ('tenant_directory', 'delta', '1970-01-01T00:00:00Z', 'success', 0),
    ('unit_directory', 'delta', '1970-01-01T00:00:00Z', 'success', 0),
    ('property_group_directory', 'delta', '1970-01-01T00:00:00Z', 'success', 0)
ON CONFLICT (endpoint) DO NOTHING;

-- Verify the entries were created
SELECT
    endpoint,
    sync_method,
    last_synced_at,
    last_run_status,
    last_row_count
FROM appfolio_sync_state
ORDER BY endpoint;
