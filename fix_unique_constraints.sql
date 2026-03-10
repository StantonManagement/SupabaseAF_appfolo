-- Fix Unique Constraints for Delta Sync Upsert
-- Run this in Supabase SQL Editor

-- =============================================================================
-- PROBLEM: Unique constraints are on wrong fields
-- =============================================================================
-- Current constraints:
--   - AF_UnitDirectory: uq_unit_directory_unit (unit_id)
--   - AF_TenantDirectory: uq_tenant_directory_occupancy (occupancy_id)
--
-- Code expects to upsert on 'id' field (primary key)
-- This causes duplicate key errors instead of updates
--
-- SOLUTION: Drop old constraints, add new ones on 'id' field
-- =============================================================================

-- 1. Drop existing incorrect constraints
ALTER TABLE "AF_UnitDirectory"
DROP CONSTRAINT IF EXISTS uq_unit_directory_unit;

ALTER TABLE "AF_TenantDirectory"
DROP CONSTRAINT IF EXISTS uq_tenant_directory_occupancy;

-- 2. Add correct unique constraints on 'id' field
-- (Assuming 'id' is the AppFolio record ID that should be unique)
ALTER TABLE "AF_UnitDirectory"
ADD CONSTRAINT uq_unit_directory_id UNIQUE (id);

ALTER TABLE "AF_TenantDirectory"
ADD CONSTRAINT uq_tenant_directory_id UNIQUE (id);

-- 3. Check AF_WorkOrder constraint (should also be on 'id')
-- First check if it exists
SELECT
    conname as constraint_name,
    a.attname as column_name
FROM pg_constraint c
JOIN pg_class t ON c.conrelid = t.oid
JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(c.conkey)
WHERE t.relname = 'AF_WorkOrder'
    AND c.contype = 'u';

-- If AF_WorkOrder doesn't have unique constraint on 'id', add it:
ALTER TABLE "AF_WorkOrder"
ADD CONSTRAINT uq_work_order_id UNIQUE (id);

-- 4. Verify new constraints
SELECT
    t.relname as table_name,
    c.conname as constraint_name,
    a.attname as column_name
FROM pg_constraint c
JOIN pg_class t ON c.conrelid = t.oid
JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(c.conkey)
WHERE t.relname IN ('AF_UnitDirectory', 'AF_TenantDirectory', 'AF_WorkOrder')
    AND c.contype = 'u'
ORDER BY t.relname, c.conname;
