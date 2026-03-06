# AppFolio Delta Sync - Implementation Summary

**Date:** March 6, 2026
**Status:** ✅ **READY FOR TESTING**

---

## What We Did

Fixed the AppFolio sync bloat issue (329K+ rows → ~1,500 rows) by implementing delta sync with timestamp-based filtering.

### Changes Made

| File | Changes | Purpose |
|------|---------|---------|
| `app/services/appfolio.py` | Added `last_synced_at` parameter, sends `updated_at_from` in request body | Fetches only changed records from AppFolio |
| `app/services/sync.py` | Calls `get_last_sync_time()` before fetching | Enables delta sync by default |
| `app/services/supabase_client.py` | Added `get_last_sync_time()`, `update_sync_state()` | Tracks sync timestamps in database |
| `jobs/sync_work_orders.py` | New scheduled job script | Work orders every 5 minutes |
| `jobs/sync_tenants.py` | New scheduled job script | Tenants hourly |
| `jobs/sync_units.py` | New scheduled job script | Units hourly |
| `jobs/sync_properties.py` | New scheduled job script | Properties daily |

### Database Infrastructure (Already Created)

From the earlier migration in MaintOC repo (`20260306_appfolio_sync_fix_safe.sql`):

- ✅ `appfolio_sync_state` table
- ✅ `get_last_sync_time()` function
- ✅ `update_sync_state()` function
- ✅ `set_sync_method()` function
- ✅ `appfolio_sync_status` view
- ✅ Unique constraints on AF_ tables

---

## How It Works

### Before (Bloat Issue)
```
Hourly Cron → Fetch ALL work orders (500 records)
            → Insert/Upsert ALL 500
            → Result: 329K rows accumulated
```

### After (Delta Sync)
```
1. Get last sync: "2026-03-06T10:00:00Z"
2. Fetch from AppFolio: only records updated AFTER that time
3. AppFolio returns: 3 changed records
4. Upsert only those 3
5. Update sync state: new timestamp stored
6. Next run: only fetches records changed since new timestamp
```

---

## Testing Locally

### Quick Test

```bash
cd /Users/zeff/Desktop/Work/stanton/SupabaseAF_appfolo

# 1. Test infrastructure
python test_delta_sync.py

# 2. Test work orders sync
python jobs/sync_work_orders.py

# 3. Run again (should show DELTA SYNC)
python jobs/sync_work_orders.py
```

### Expected Output (First Run)

```
============================================================
WORK ORDERS SYNC - Every 5 minutes
============================================================
⚡ INITIATING SYNC PROCESS FOR DATASET: 'work_order'
📅 No previous sync found for 'work_order'
🌐 FETCHING DATA FROM APPFOLIO API (FULL SYNC)
✅ SUCCESSFULLY FETCHED 247 RECORDS FROM APPFOLIO
✅ SYNC COMPLETE FOR DATASET 'work_order':
  - ✅ Success: 247
  - ❌ Failed: 0
  - 📊 Total: 247
✅ Updated sync state for 'work_order': 247 rows, status=success
```

### Expected Output (Second Run - Delta Sync)

```
============================================================
WORK ORDERS SYNC - Every 5 minutes
============================================================
⚡ INITIATING SYNC PROCESS FOR DATASET: 'work_order'
📅 Last sync for 'work_order': 2026-03-06T15:23:45.123456+00:00
📅 Last sync: 2026-03-06T15:23:45.123456+00:00 - Using DELTA sync
🌐 FETCHING DATA FROM APPFOLIO API (DELTA SYNC since 2026-03-06T15:23:45.123456+00:00)
📅 Applying date filter: updated_at_from=2026-03-06T15:23:45.123456+00:00
✅ SUCCESSFULLY FETCHED 0 RECORDS FROM APPFOLIO
✅ SYNC COMPLETE FOR DATASET 'work_order':
  - ✅ Success: 0
  - ❌ Failed: 0
  - 📊 Total: 0
✅ Updated sync state for 'work_order': 0 rows, status=success
```

If you see **"DELTA SYNC"** and **"0 RECORDS"** (or small number), delta sync is working! ✅

---

## Deployment to Railway

### Step 1: Commit & Push

```bash
cd /Users/zeff/Desktop/Work/stanton/SupabaseAF_appfolo

git add .
git commit -m "feat: implement delta sync with date filtering

- Add last_synced_at parameter to AppFolio API requests
- Track sync state in appfolio_sync_state table
- Create scheduled job scripts for different frequencies
- Work orders: 5 min, Tenants/Units: hourly, Properties: daily"

git push origin main
```

### Step 2: Railway Auto-Deploys

Railway will automatically detect the push and deploy. Check logs:

```bash
# In Railway dashboard, click "View Logs"
# Or use CLI:
railway logs --follow
```

### Step 3: Set Up Cron Jobs

**In Railway Dashboard:**

1. Go to your service
2. Click "Settings" → "Cron Jobs" (or "Deployments" → "Cron")
3. Add these schedules:

| Schedule | Command | Description |
|----------|---------|-------------|
| `*/5 * * * *` | `python /app/jobs/sync_work_orders.py` | Work orders every 5 minutes |
| `0 * * * *` | `python /app/jobs/sync_tenants.py` | Tenants hourly |
| `0 * * * *` | `python /app/jobs/sync_units.py` | Units hourly |
| `0 5 * * *` | `python /app/jobs/sync_properties.py` | Properties daily at midnight EST |

**Note:** If Railway doesn't support cron on your plan, use external service like **cron-job.org** to hit HTTP endpoints.

---

## Monitoring

### Check Sync Status in Supabase

```sql
-- View all sync states
SELECT * FROM appfolio_sync_status ORDER BY last_synced_at DESC;

-- Check specific endpoint
SELECT * FROM appfolio_sync_state WHERE endpoint = 'work_order';

-- Monitor row counts (should stay stable)
SELECT
  'AF_WorkOrder' as table_name, COUNT(*) as rows FROM "AF_WorkOrder"
UNION ALL
SELECT 'AF_TenantDirectory', COUNT(*) FROM "AF_TenantDirectory"
UNION ALL
SELECT 'AF_UnitDirectory', COUNT(*) FROM "AF_UnitDirectory"
UNION ALL
SELECT 'AF_buildings', COUNT(*) FROM "AF_buildings";
```

### Expected Row Counts

| Table | Expected Rows | Previous (Bloated) |
|-------|---------------|---------------------|
| AF_WorkOrder | ~100-500 | 155,543 |
| AF_TenantDirectory | ~433 | 0 (was truncated) |
| AF_UnitDirectory | ~323 | 323 |
| AF_buildings | 66 | 66 |
| **TOTAL** | **~1,500** | **329K+** |

---

## Troubleshooting

### Problem: "FULL SYNC" every time (never shows "DELTA SYNC")

**Cause:** `updated_at_from` filter not supported by AppFolio API for this dataset.

**Solution:**
1. Check Railway logs for API errors (400/422 status)
2. If not supported, disable delta for that dataset:

```python
# In jobs/sync_whatever.py, change:
result = sync_details("dataset_name", use_delta=False)
```

### Problem: Sync state not updating

**Cause:** RPC function call failing.

**Solution:**
```sql
-- Verify function exists
SELECT proname FROM pg_proc WHERE proname = 'update_sync_state';

-- Test manually
SELECT update_sync_state('test', 100, 'success');
```

### Problem: Railway cron not working

**Cause:** Railway free tier might not support native cron.

**Solution:** Use external cron service:
1. Sign up at cron-job.org
2. Create jobs to hit: `POST https://your-app.railway.app/sync_details`
3. Body: `{"dataset": "work_order"}`

---

## Next Actions for You

### 1. Test Locally (5 minutes)

```bash
cd /Users/zeff/Desktop/Work/stanton/SupabaseAF_appfolo
python test_delta_sync.py
python jobs/sync_work_orders.py
```

### 2. Deploy to Railway (10 minutes)

```bash
git add .
git commit -m "feat: implement delta sync"
git push origin main
```

### 3. Set Up Cron (5 minutes)

Configure Railway cron jobs or external cron service.

### 4. Monitor (24-48 hours)

Check:
- Railway logs show "DELTA SYNC"
- Row counts stay stable
- No errors in logs
- Sync state table updates

---

## Success Criteria

✅ **You know it's working when:**

1. First sync logs show: `FULL SYNC` and large record count (247+)
2. Second sync logs show: `DELTA SYNC` and small/zero record count (0-5)
3. Sync state table updates after each run
4. Row counts remain stable (~1,500 total)
5. No accumulation over time

---

## Files Created/Modified

**Modified:**
- `app/services/appfolio.py`
- `app/services/sync.py`
- `app/services/supabase_client.py`

**Created:**
- `jobs/sync_work_orders.py`
- `jobs/sync_tenants.py`
- `jobs/sync_units.py`
- `jobs/sync_properties.py`
- `test_delta_sync.py`
- `DELTA_SYNC_IMPLEMENTATION.md` (full guide)
- `IMPLEMENTATION_SUMMARY.md` (this file)

---

## Questions?

If anything fails or you need clarification:
1. Check logs: `railway logs` or Railway dashboard
2. Check Supabase sync state: `SELECT * FROM appfolio_sync_status;`
3. Verify database functions exist: Run migration status check

---

**Ready to proceed!** Start with local testing, then deploy to Railway. 🚀
