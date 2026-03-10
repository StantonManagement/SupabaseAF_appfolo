-- Verify Delta Sync Status
-- Run this in Supabase SQL Editor

-- =============================================================================
-- 1. Check Sync State (Last sync times and status)
-- =============================================================================
SELECT
  '=== SYNC STATE ===' as section,
  '' as endpoint,
  '' as last_synced,
  '' as status,
  '' as method;

SELECT
  endpoint,
  last_synced_at::TEXT as last_synced,
  last_run_status as status,
  sync_method as method,
  last_row_count as rows_synced,
  CASE
    WHEN last_synced_at > NOW() - INTERVAL '10 minutes' THEN '🟢 Recent'
    WHEN last_synced_at > NOW() - INTERVAL '1 hour' THEN '🟡 Within hour'
    WHEN last_synced_at > NOW() - INTERVAL '1 day' THEN '🟠 Within day'
    ELSE '🔴 Stale'
  END as freshness
FROM appfolio_sync_state
ORDER BY last_synced_at DESC;

-- =============================================================================
-- 2. Check Row Counts (Should stay stable ~1,500 total)
-- =============================================================================
SELECT
  '' as section,
  '=== ROW COUNTS ===' as table_name,
  '' as current_rows,
  '' as status;

SELECT
  '' as section,
  'AF_WorkOrder' as table_name,
  COUNT(*)::TEXT as current_rows,
  CASE
    WHEN COUNT(*) < 1000 THEN '✅ Good'
    WHEN COUNT(*) < 5000 THEN '⚠️ Growing'
    ELSE '❌ Bloated'
  END as status
FROM "AF_WorkOrder"

UNION ALL

SELECT
  '',
  'AF_TenantDirectory',
  COUNT(*)::TEXT,
  CASE
    WHEN COUNT(*) < 1000 THEN '✅ Good'
    WHEN COUNT(*) < 5000 THEN '⚠️ Growing'
    ELSE '❌ Bloated'
  END
FROM "AF_TenantDirectory"

UNION ALL

SELECT
  '',
  'AF_UnitDirectory',
  COUNT(*)::TEXT,
  CASE
    WHEN COUNT(*) < 1000 THEN '✅ Good'
    WHEN COUNT(*) < 5000 THEN '⚠️ Growing'
    ELSE '❌ Bloated'
  END
FROM "AF_UnitDirectory"

UNION ALL

SELECT
  '',
  'AF_buildings',
  COUNT(*)::TEXT,
  CASE
    WHEN COUNT(*) < 500 THEN '✅ Good'
    WHEN COUNT(*) < 1000 THEN '⚠️ Growing'
    ELSE '❌ Bloated'
  END
FROM "AF_buildings"

UNION ALL

SELECT
  '',
  '📊 TOTAL',
  (
    (SELECT COUNT(*) FROM "AF_WorkOrder") +
    (SELECT COUNT(*) FROM "AF_TenantDirectory") +
    (SELECT COUNT(*) FROM "AF_UnitDirectory") +
    (SELECT COUNT(*) FROM "AF_buildings")
  )::TEXT,
  CASE
    WHEN (
      (SELECT COUNT(*) FROM "AF_WorkOrder") +
      (SELECT COUNT(*) FROM "AF_TenantDirectory") +
      (SELECT COUNT(*) FROM "AF_UnitDirectory") +
      (SELECT COUNT(*) FROM "AF_buildings")
    ) < 3000 THEN '✅ Healthy'
    WHEN (
      (SELECT COUNT(*) FROM "AF_WorkOrder") +
      (SELECT COUNT(*) FROM "AF_TenantDirectory") +
      (SELECT COUNT(*) FROM "AF_UnitDirectory") +
      (SELECT COUNT(*) FROM "AF_buildings")
    ) < 10000 THEN '⚠️ Monitor'
    ELSE '❌ BLOATED (Fix needed!)'
  END;

-- =============================================================================
-- 3. Check for Recent Syncs (Last 24 hours)
-- =============================================================================
SELECT
  '' as section,
  '=== RECENT ACTIVITY ===' as info,
  '' as count;

SELECT
  '' as section,
  'Endpoints synced today' as info,
  COUNT(*)::TEXT as count
FROM appfolio_sync_state
WHERE last_synced_at > NOW() - INTERVAL '24 hours';

-- =============================================================================
-- 4. Readiness Check
-- =============================================================================
SELECT
  '' as section,
  '=== READINESS CHECK ===' as check_item,
  '' as status;

SELECT
  '',
  'Delta sync infrastructure' as check_item,
  CASE
    WHEN EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'get_last_sync_time')
      AND EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'update_sync_state')
    THEN '✅ Ready'
    ELSE '❌ Missing functions'
  END as status

UNION ALL

SELECT
  '',
  'Unique constraints for upsert',
  CASE
    WHEN EXISTS (
      SELECT 1 FROM pg_constraint c
      JOIN pg_class t ON c.conrelid = t.oid
      WHERE t.relname IN ('AF_WorkOrder', 'AF_TenantDirectory', 'AF_UnitDirectory', 'AF_buildings')
        AND c.contype = 'u'
    )
    THEN '✅ Configured'
    ELSE '⚠️ Some missing'
  END

UNION ALL

SELECT
  '',
  'Table bloat status',
  CASE
    WHEN (
      (SELECT COUNT(*) FROM "AF_WorkOrder") +
      (SELECT COUNT(*) FROM "AF_TenantDirectory") +
      (SELECT COUNT(*) FROM "AF_UnitDirectory") +
      (SELECT COUNT(*) FROM "AF_buildings")
    ) < 3000
    THEN '✅ Healthy (<3K rows)'
    ELSE '⚠️ Monitor (>3K rows)'
  END;
