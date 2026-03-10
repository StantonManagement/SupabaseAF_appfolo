-- Quick Check: Are AF Tables Fixed?
-- Run this in Supabase SQL Editor to verify the fix

-- =============================================================================
-- 1. CHECK ROW COUNTS (Should be ~1,500 total if fixed)
-- =============================================================================
SELECT
  '=== CURRENT ROW COUNTS ===' as section,
  '' as table_name,
  '' as current_rows,
  '' as status;

SELECT
  '',
  'AF_WorkOrder' as table_name,
  COUNT(*)::TEXT as current_rows,
  CASE
    WHEN COUNT(*) < 1000 THEN '✅ Good'
    WHEN COUNT(*) < 5000 THEN '⚠️ Growing'
    WHEN COUNT(*) > 100000 THEN '❌ STILL BLOATED!'
    ELSE '🔴 Check needed'
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
    ) < 3000 THEN '✅ FIXED!'
    WHEN (
      (SELECT COUNT(*) FROM "AF_WorkOrder") +
      (SELECT COUNT(*) FROM "AF_TenantDirectory") +
      (SELECT COUNT(*) FROM "AF_UnitDirectory") +
      (SELECT COUNT(*) FROM "AF_buildings")
    ) < 10000 THEN '⚠️ Monitor'
    ELSE '❌ STILL BLOATED!'
  END;

-- =============================================================================
-- 2. CHECK FOR DUPLICATES (Should be 0 if fixed properly)
-- =============================================================================
SELECT
  '' as section,
  '=== DUPLICATE CHECK ===' as info,
  '' as count;

SELECT
  '',
  'AF_WorkOrder duplicates' as info,
  COUNT(*)::TEXT as count
FROM (
  SELECT id
  FROM "AF_WorkOrder"
  GROUP BY id
  HAVING COUNT(*) > 1
) duplicates;

-- =============================================================================
-- 3. CHECK SYNC STATE (Is delta sync running?)
-- =============================================================================
SELECT
  '' as section,
  '=== SYNC STATE ===' as endpoint,
  '' as last_synced,
  '' as status,
  '' as method;

SELECT
  '',
  endpoint,
  last_synced_at::TEXT as last_synced,
  last_run_status as status,
  sync_method as method
FROM appfolio_sync_state
WHERE endpoint IN ('work_order', 'tenant_directory', 'unit_directory', 'property_group_directory')
ORDER BY last_synced_at DESC;

-- =============================================================================
-- 4. CHECK MOST RECENT RECORDS (Are they current?)
-- =============================================================================
SELECT
  '' as section,
  '=== RECENT DATA CHECK ===' as info,
  '' as latest_record;

SELECT
  '',
  'AF_WorkOrder latest' as info,
  MAX(updated_at)::TEXT as latest_record
FROM "AF_WorkOrder";

-- =============================================================================
-- 5. VERDICT
-- =============================================================================
SELECT
  '=== VERDICT ===' as result,
  CASE
    WHEN (
      (SELECT COUNT(*) FROM "AF_WorkOrder") +
      (SELECT COUNT(*) FROM "AF_TenantDirectory") +
      (SELECT COUNT(*) FROM "AF_UnitDirectory") +
      (SELECT COUNT(*) FROM "AF_buildings")
    ) < 3000
    AND (SELECT COUNT(*) FROM (
      SELECT id FROM "AF_WorkOrder" GROUP BY id HAVING COUNT(*) > 1
    ) dups) = 0
    THEN '✅ YES - Tables are fixed! Row counts healthy, no duplicates.'

    WHEN (
      (SELECT COUNT(*) FROM "AF_WorkOrder") +
      (SELECT COUNT(*) FROM "AF_TenantDirectory") +
      (SELECT COUNT(*) FROM "AF_UnitDirectory") +
      (SELECT COUNT(*) FROM "AF_buildings")
    ) > 100000
    THEN '❌ NO - Still bloated! Over 100K rows. Not fixed.'

    ELSE '⚠️ PARTIALLY - Some improvement but needs monitoring.'
  END as assessment;
