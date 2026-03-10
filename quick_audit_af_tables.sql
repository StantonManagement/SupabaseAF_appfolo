-- Quick Audit: All AF Tables
-- Run this in Supabase SQL Editor for a fast overview

-- =============================================================================
-- QUICK ROW COUNT SUMMARY
-- =============================================================================

-- Method 1: Check specific known tables
SELECT
  'AF_WorkOrder' as table_name,
  COUNT(*) as rows,
  CASE
    WHEN COUNT(*) < 1000 THEN '✅ Good'
    WHEN COUNT(*) < 10000 THEN '⚠️ Monitor'
    ELSE '❌ Bloated'
  END as status
FROM "AF_WorkOrder"

UNION ALL

SELECT 'AF_TenantDirectory', COUNT(*),
  CASE WHEN COUNT(*) < 1000 THEN '✅ Good' WHEN COUNT(*) < 10000 THEN '⚠️ Monitor' ELSE '❌ Bloated' END
FROM "AF_TenantDirectory"

UNION ALL

SELECT 'AF_UnitDirectory', COUNT(*),
  CASE WHEN COUNT(*) < 1000 THEN '✅ Good' WHEN COUNT(*) < 10000 THEN '⚠️ Monitor' ELSE '❌ Bloated' END
FROM "AF_UnitDirectory"

UNION ALL

SELECT 'AF_buildings', COUNT(*),
  CASE WHEN COUNT(*) < 500 THEN '✅ Good' WHEN COUNT(*) < 5000 THEN '⚠️ Monitor' ELSE '❌ Bloated' END
FROM "AF_buildings"

UNION ALL

SELECT 'AF_RentRoll', COUNT(*),
  CASE WHEN COUNT(*) < 1000 THEN '✅ Good' WHEN COUNT(*) < 10000 THEN '⚠️ Monitor' ELSE '❌ Bloated' END
FROM "AF_RentRoll"

UNION ALL

SELECT 'AF_Delinquency', COUNT(*),
  CASE WHEN COUNT(*) < 1000 THEN '✅ Good' WHEN COUNT(*) < 10000 THEN '⚠️ Monitor' ELSE '❌ Bloated' END
FROM "AF_Delinquency"

UNION ALL

SELECT 'AF_VendorDirectory', COUNT(*),
  CASE WHEN COUNT(*) < 1000 THEN '✅ Good' WHEN COUNT(*) < 5000 THEN '⚠️ Monitor' ELSE '❌ Bloated' END
FROM "AF_VendorDirectory"

UNION ALL

SELECT '📊 TOTAL (all above)',
  (SELECT COUNT(*) FROM "AF_WorkOrder") +
  (SELECT COUNT(*) FROM "AF_TenantDirectory") +
  (SELECT COUNT(*) FROM "AF_UnitDirectory") +
  (SELECT COUNT(*) FROM "AF_buildings") +
  (SELECT COUNT(*) FROM "AF_RentRoll") +
  (SELECT COUNT(*) FROM "AF_Delinquency") +
  (SELECT COUNT(*) FROM "AF_VendorDirectory"),
  CASE
    WHEN (
      (SELECT COUNT(*) FROM "AF_WorkOrder") +
      (SELECT COUNT(*) FROM "AF_TenantDirectory") +
      (SELECT COUNT(*) FROM "AF_UnitDirectory") +
      (SELECT COUNT(*) FROM "AF_buildings") +
      (SELECT COUNT(*) FROM "AF_RentRoll") +
      (SELECT COUNT(*) FROM "AF_Delinquency") +
      (SELECT COUNT(*) FROM "AF_VendorDirectory")
    ) < 10000 THEN '✅ Healthy'
    ELSE '⚠️ Monitor'
  END

ORDER BY rows DESC;

-- =============================================================================
-- CHECK FOR DUPLICATES IN KEY TABLES
-- =============================================================================

-- Work Orders duplicates
SELECT
  'AF_WorkOrder duplicates' as check_type,
  COUNT(*) as duplicate_groups,
  SUM(dup_count - 1) as extra_rows
FROM (
  SELECT work_order_id, COUNT(*) as dup_count
  FROM "AF_WorkOrder"
  GROUP BY work_order_id
  HAVING COUNT(*) > 1
) dups

UNION ALL

-- Tenants duplicates
SELECT
  'AF_TenantDirectory duplicates',
  COUNT(*),
  SUM(dup_count - 1)
FROM (
  SELECT occupancy_id, COUNT(*) as dup_count
  FROM "AF_TenantDirectory"
  GROUP BY occupancy_id
  HAVING COUNT(*) > 1
) dups

UNION ALL

-- Units duplicates
SELECT
  'AF_UnitDirectory duplicates',
  COUNT(*),
  SUM(dup_count - 1)
FROM (
  SELECT unit_id, COUNT(*) as dup_count
  FROM "AF_UnitDirectory"
  GROUP BY unit_id
  HAVING COUNT(*) > 1
) dups;

-- =============================================================================
-- LIST ALL AF_ TABLES THAT EXIST
-- =============================================================================

SELECT
  tablename as af_table,
  NULL as estimated_rows
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename LIKE 'AF_%'
ORDER BY tablename;

-- =============================================================================
-- SYNC STATE OVERVIEW
-- =============================================================================

SELECT
  endpoint,
  last_synced_at,
  last_run_status,
  last_row_count,
  sync_method,
  CASE
    WHEN last_synced_at > NOW() - INTERVAL '1 hour' THEN '🟢 Recent'
    WHEN last_synced_at > NOW() - INTERVAL '1 day' THEN '🟡 Today'
    WHEN last_synced_at > NOW() - INTERVAL '7 days' THEN '🟠 This week'
    WHEN last_synced_at < '1971-01-01' THEN '⚪ Never'
    ELSE '🔴 Old'
  END as freshness
FROM appfolio_sync_state
ORDER BY last_synced_at DESC NULLS LAST;
