-- Complete Audit of All AF Tables
-- Run this in Supabase SQL Editor

-- =============================================================================
-- 1. List ALL AF_ tables in database
-- =============================================================================
SELECT
  '=== ALL AF TABLES IN DATABASE ===' as section,
  '' as table_name,
  '' as row_count,
  '' as has_unique_constraint,
  '' as unique_field;

SELECT
  '',
  tablename as table_name,
  NULL::TEXT as row_count,
  '' as has_unique_constraint,
  '' as unique_field
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename LIKE 'AF_%'
ORDER BY tablename;

-- =============================================================================
-- 2. Get row counts for ALL AF_ tables
-- =============================================================================
SELECT
  '' as section,
  '=== ROW COUNTS FOR ALL AF TABLES ===' as table_name,
  '' as rows,
  '' as status;

-- This will dynamically count all AF_ tables
DO $$
DECLARE
  r RECORD;
  row_count INTEGER;
BEGIN
  FOR r IN
    SELECT tablename
    FROM pg_tables
    WHERE schemaname = 'public'
      AND tablename LIKE 'AF_%'
    ORDER BY tablename
  LOOP
    EXECUTE format('SELECT COUNT(*) FROM %I', r.tablename) INTO row_count;
    RAISE NOTICE '%, %', r.tablename, row_count;
  END LOOP;
END $$;

-- =============================================================================
-- 3. Check unique constraints on ALL AF_ tables
-- =============================================================================
SELECT
  '' as section,
  '=== UNIQUE CONSTRAINTS ===' as table_name,
  '' as constraint_name,
  '' as column_name;

SELECT
  '',
  t.relname as table_name,
  c.conname as constraint_name,
  string_agg(a.attname, ', ') as column_name
FROM pg_constraint c
JOIN pg_class t ON c.conrelid = t.oid
JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(c.conkey)
WHERE t.relname LIKE 'AF_%'
  AND c.contype = 'u'
GROUP BY t.relname, c.conname
ORDER BY t.relname;

-- =============================================================================
-- 4. Check for tables with MANY rows (potential bloat)
-- =============================================================================
SELECT
  '' as section,
  '=== TABLES WITH HIGH ROW COUNTS ===' as table_name,
  '' as rows,
  '' as status;

-- Manual check for specific large tables
SELECT
  '',
  'AF_WorkOrder' as table_name,
  COUNT(*)::TEXT as rows,
  CASE
    WHEN COUNT(*) < 1000 THEN '✅ Good'
    WHEN COUNT(*) < 10000 THEN '⚠️ Monitor'
    WHEN COUNT(*) < 100000 THEN '🔴 High'
    ELSE '❌ BLOATED!'
  END as status
FROM "AF_WorkOrder"

UNION ALL

SELECT '', 'AF_TenantDirectory', COUNT(*)::TEXT,
  CASE WHEN COUNT(*) < 1000 THEN '✅ Good' WHEN COUNT(*) < 10000 THEN '⚠️ Monitor' ELSE '🔴 High' END
FROM "AF_TenantDirectory"

UNION ALL

SELECT '', 'AF_UnitDirectory', COUNT(*)::TEXT,
  CASE WHEN COUNT(*) < 1000 THEN '✅ Good' WHEN COUNT(*) < 10000 THEN '⚠️ Monitor' ELSE '🔴 High' END
FROM "AF_UnitDirectory"

UNION ALL

SELECT '', 'AF_buildings', COUNT(*)::TEXT,
  CASE WHEN COUNT(*) < 500 THEN '✅ Good' WHEN COUNT(*) < 5000 THEN '⚠️ Monitor' ELSE '🔴 High' END
FROM "AF_buildings";

-- Add more tables as needed

-- =============================================================================
-- 5. Check for DUPLICATE records in critical tables
-- =============================================================================
SELECT
  '' as section,
  '=== DUPLICATE CHECK ===' as table_name,
  '' as field,
  '' as duplicate_count;

-- Check Work Orders
SELECT
  '',
  'AF_WorkOrder' as table_name,
  'work_order_id' as field,
  COUNT(*)::TEXT as duplicate_count
FROM (
  SELECT work_order_id
  FROM "AF_WorkOrder"
  GROUP BY work_order_id
  HAVING COUNT(*) > 1
) dups

UNION ALL

-- Check Tenants
SELECT
  '',
  'AF_TenantDirectory',
  'occupancy_id',
  COUNT(*)::TEXT
FROM (
  SELECT occupancy_id
  FROM "AF_TenantDirectory"
  GROUP BY occupancy_id
  HAVING COUNT(*) > 1
) dups

UNION ALL

-- Check Units
SELECT
  '',
  'AF_UnitDirectory',
  'unit_id',
  COUNT(*)::TEXT
FROM (
  SELECT unit_id
  FROM "AF_UnitDirectory"
  GROUP BY unit_id
  HAVING COUNT(*) > 1
) dups;

-- =============================================================================
-- 6. Check sync state for all endpoints
-- =============================================================================
SELECT
  '' as section,
  '=== SYNC STATE FOR ALL ENDPOINTS ===' as endpoint,
  '' as last_synced,
  '' as status,
  '' as row_count,
  '' as method;

SELECT
  '',
  endpoint,
  last_synced_at::TEXT as last_synced,
  last_run_status as status,
  last_row_count::TEXT as row_count,
  sync_method as method
FROM appfolio_sync_state
ORDER BY last_synced_at DESC NULLS LAST;

-- =============================================================================
-- 7. Tables that exist in database but NOT in sync state
-- =============================================================================
SELECT
  '' as section,
  '=== TABLES NOT TRACKED IN SYNC STATE ===' as table_name,
  '' as row_count;

SELECT
  '',
  tablename as table_name,
  NULL::TEXT as row_count
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename LIKE 'AF_%'
  AND LOWER(REPLACE(tablename, 'AF_', '')) NOT IN (
    SELECT LOWER(endpoint) FROM appfolio_sync_state
  )
ORDER BY tablename;

-- =============================================================================
-- 8. Summary Statistics
-- =============================================================================
SELECT
  '' as section,
  '=== SUMMARY ===' as metric,
  '' as count;

SELECT
  '',
  'Total AF_ tables in database' as metric,
  COUNT(*)::TEXT as count
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename LIKE 'AF_%'

UNION ALL

SELECT
  '',
  'Tables with scheduled syncs',
  COUNT(*)::TEXT
FROM appfolio_sync_state
WHERE last_synced_at > '1970-01-01'

UNION ALL

SELECT
  '',
  'Tables with unique constraints',
  COUNT(DISTINCT t.relname)::TEXT
FROM pg_constraint c
JOIN pg_class t ON c.conrelid = t.oid
WHERE t.relname LIKE 'AF_%'
  AND c.contype = 'u'

UNION ALL

SELECT
  '',
  'Total rows across all AF_ tables',
  (
    (SELECT COUNT(*) FROM "AF_WorkOrder") +
    (SELECT COUNT(*) FROM "AF_TenantDirectory") +
    (SELECT COUNT(*) FROM "AF_UnitDirectory") +
    (SELECT COUNT(*) FROM "AF_buildings")
    -- Add more tables as discovered
  )::TEXT;

-- =============================================================================
-- 9. Recommendations
-- =============================================================================
SELECT
  '' as section,
  '=== RECOMMENDATIONS ===' as recommendation;

SELECT
  '',
  CASE
    WHEN (SELECT COUNT(*) FROM "AF_WorkOrder") > 10000
    THEN '⚠️ AF_WorkOrder has high row count - check for bloat'
    WHEN (SELECT COUNT(*) FROM "AF_WorkOrder") < 1000
    THEN '✅ AF_WorkOrder row count is healthy'
    ELSE 'ℹ️ AF_WorkOrder row count is acceptable'
  END as recommendation

UNION ALL

SELECT
  '',
  CASE
    WHEN EXISTS (
      SELECT 1 FROM "AF_WorkOrder"
      GROUP BY work_order_id
      HAVING COUNT(*) > 1
      LIMIT 1
    )
    THEN '❌ AF_WorkOrder has duplicate work_order_ids - needs cleanup'
    ELSE '✅ AF_WorkOrder has no duplicates'
  END;

-- Add more recommendations as needed
