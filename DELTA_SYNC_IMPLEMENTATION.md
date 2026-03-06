# Delta Sync Implementation Guide

**Date:** March 6, 2026
**Status:** ✅ Implemented - Ready for Testing & Deployment

---

## Overview

This implementation adds **delta sync** capabilities to the AppFolio → Supabase sync service to prevent table bloat (previously 329K+ rows, now maintaining ~1,500 rows).

### What Changed

**Before:**
- Every sync fetched ALL records from AppFolio
- Used `.upsert()` but still processed thousands of records each time
- Hourly sync = 329K accumulated rows in AF_RentRoll

**After:**
- Delta sync fetches ONLY records modified since last sync
- Stores last sync timestamp in `appfolio_sync_state` table
- Upserts only changed records
- Different sync frequencies per dataset (5 min / hourly / daily)

---

## Architecture

### Delta Sync Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Get Last Sync Time                                      │
│    SELECT get_last_sync_time('work_order')                 │
│    → Returns: "2026-03-06T10:00:00Z"                       │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Fetch from AppFolio Reports API v2                      │
│    POST /api/v2/reports/work_order                         │
│    Body: { "updated_at_from": "2026-03-06T10:00:00Z" }    │
│    → Returns: 5 changed work orders                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Upsert to Supabase                                      │
│    INSERT INTO "AF_WorkOrder" ... ON CONFLICT UPDATE       │
│    → Updates 5 records, leaves others untouched            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Update Sync State                                       │
│    SELECT update_sync_state('work_order', 5, 'success')   │
│    → Stores new timestamp for next delta sync              │
└─────────────────────────────────────────────────────────────┘
```

---

## Files Modified

### 1. `app/services/appfolio.py`

**Changes:**
- Added `last_synced_at` parameter to `get_appfolio_details()`
- Sends `updated_at_from` filter in request body for Reports API v2

```python
# Before
def get_appfolio_details(dataset: str):
    response = requests.post(f"{V2_BASE_URL}/{source_dataset}", ...)

# After
def get_appfolio_details(dataset: str, last_synced_at: str = None):
    request_body = {}
    if last_synced_at:
        request_body["updated_at_from"] = last_synced_at
    response = requests.post(f"{V2_BASE_URL}/{source_dataset}", json=request_body, ...)
```

### 2. `app/services/sync.py`

**Changes:**
- Added `use_delta` parameter (default: `True`)
- Calls `get_last_sync_time()` before fetching from AppFolio

```python
def sync_details(dataset: str, use_delta: bool = True):
    last_synced_at = None
    if use_delta:
        last_synced_at = get_last_sync_time(dataset)
    appfolio_results = get_appfolio_details(dataset, last_synced_at)
    ...
```

### 3. `app/services/supabase_client.py`

**Changes:**
- Added `get_last_sync_time()` - Calls Supabase RPC function
- Added `update_sync_state()` - Updates sync timestamp after each run
- Modified `update_supabase_details()` - Calls `update_sync_state()` at the end

```python
def get_last_sync_time(dataset: str):
    result = supabase.rpc("get_last_sync_time", {"p_endpoint": dataset}).execute()
    return result.data

def update_sync_state(dataset: str, row_count: int, status: str = "success"):
    supabase.rpc("update_sync_state", {
        "p_endpoint": dataset,
        "p_row_count": row_count,
        "p_status": status
    }).execute()
```

### 4. New Files: `jobs/*.py`

Created individual job scripts for scheduled syncs:

- `jobs/sync_work_orders.py` - Every 5 minutes (CRITICAL for emergencies)
- `jobs/sync_tenants.py` - Hourly
- `jobs/sync_units.py` - Hourly
- `jobs/sync_properties.py` - Daily

---

## Database Infrastructure

The following database objects were created in the earlier migration (`20260306_appfolio_sync_fix_safe.sql`):

### Table: `appfolio_sync_state`

```sql
CREATE TABLE appfolio_sync_state (
  endpoint TEXT PRIMARY KEY,
  last_synced_at TIMESTAMPTZ NOT NULL,
  last_run_status TEXT CHECK (last_run_status IN ('success', 'failed', 'in_progress')),
  sync_method TEXT CHECK (sync_method IN ('delta', 'full_replace', 'unknown')),
  delta_supported BOOLEAN DEFAULT false,
  last_row_count INT,
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Functions

**`get_last_sync_time(p_endpoint TEXT)`**
- Returns last successful sync timestamp
- Defaults to 30 days ago if never synced

**`update_sync_state(p_endpoint TEXT, p_row_count INT, p_status TEXT)`**
- Updates sync timestamp to NOW()
- Records row count and status

**`set_sync_method(p_endpoint TEXT, p_method TEXT, p_supported BOOLEAN)`**
- Sets delta_supported flag and sync_method

### View: `appfolio_sync_status`

```sql
SELECT * FROM appfolio_sync_status;
```

Shows current sync state for all endpoints with human-readable formatting.

---

## Sync Frequencies

| Dataset | Frequency | Reason |
|---------|-----------|--------|
| **work_order** | **Every 5 minutes** | 🚨 CRITICAL: Emergency maintenance (burst pipes, HVAC, etc.) |
| tenant_directory | Hourly | New move-ins, contact updates |
| unit_directory | Hourly | Vacancies, unit status changes |
| property_group_directory | Daily | Properties added every 3 months |
| buildings | Daily | Uses property transformation |

---

## Testing Locally

### 1. Test Individual Dataset Sync

```bash
cd /Users/zeff/Desktop/Work/stanton/SupabaseAF_appfolo

# Test work orders (delta sync)
python jobs/sync_work_orders.py

# Test tenants (delta sync)
python jobs/sync_tenants.py

# Test units (delta sync)
python jobs/sync_units.py

# Test properties (delta sync)
python jobs/sync_properties.py
```

**Expected Output:**

First run (no previous sync):
```
📅 No previous sync found for 'work_order'
🌐 FETCHING DATA FROM APPFOLIO API (FULL SYNC)
✅ SYNC COMPLETE FOR DATASET 'work_order':
  - ✅ Success: 247
  - ❌ Failed: 0
  - 📊 Total: 247
✅ Updated sync state for 'work_order': 247 rows, status=success
```

Second run (delta sync):
```
📅 Last sync for 'work_order': 2026-03-06T15:00:00Z
🌐 FETCHING DATA FROM APPFOLIO API (DELTA SYNC since 2026-03-06T15:00:00Z)
📅 Applying date filter: updated_at_from=2026-03-06T15:00:00Z
✅ SYNC COMPLETE FOR DATASET 'work_order':
  - ✅ Success: 3
  - ❌ Failed: 0
  - 📊 Total: 3
✅ Updated sync state for 'work_order': 3 rows, status=success
```

### 2. Verify Sync State

Run this SQL in Supabase SQL Editor:

```sql
-- Check all sync states
SELECT * FROM appfolio_sync_status ORDER BY last_synced_at DESC;

-- Check specific endpoint
SELECT * FROM appfolio_sync_state WHERE endpoint = 'work_order';

-- Check row counts
SELECT
  'AF_WorkOrder' as table_name, COUNT(*) as rows FROM "AF_WorkOrder"
UNION ALL
SELECT 'AF_TenantDirectory', COUNT(*) FROM "AF_TenantDirectory"
UNION ALL
SELECT 'AF_UnitDirectory', COUNT(*) FROM "AF_UnitDirectory";
```

---

## Railway Deployment

### Step 1: Push Changes to GitHub

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

### Step 2: Railway Will Auto-Deploy

Railway is already connected to your GitHub repo. After pushing, it will:
1. Detect the push
2. Build the new image
3. Deploy automatically

Check logs in Railway dashboard: https://railway.app/project/your-project-id

### Step 3: Set Up Cron Jobs in Railway

**Option A: Railway Cron (Recommended)**

In Railway dashboard:
1. Go to your service
2. Click "Settings" → "Cron Jobs"
3. Add these schedules:

```bash
# Work orders - Every 5 minutes
*/5 * * * * python /app/jobs/sync_work_orders.py

# Tenants - Hourly
0 * * * * python /app/jobs/sync_tenants.py

# Units - Hourly
0 * * * * python /app/jobs/sync_units.py

# Properties - Daily at midnight EST
0 5 * * * python /app/jobs/sync_properties.py
```

**Option B: External Cron Service (Alternative)**

Use a service like cron-job.org or EasyCron to hit HTTP endpoints:

```bash
# Every 5 minutes
POST https://your-railway-app.railway.app/sync_details
Body: {"dataset": "work_order"}

# Hourly
POST https://your-railway-app.railway.app/sync_details
Body: {"dataset": "tenant_directory"}
```

### Step 4: Environment Variables

Verify these are set in Railway (already configured):

```
APPFOLIO_CLIENT_ID=7986fe0a73132b6dc3879bbc5d8ee4c8
APPFOLIO_CLIENT_SECRET=397b9c151d85dbe670075dddb8d8e29d
SUPABASE_URL=https://wkwmxxlfheywwbgdbzxe.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
V1_BASE_URL=https://stantonmgmt.appfolio.com/api/v1
V2_BASE_URL=https://stantonmgmt.appfolio.com/api/v2/reports
```

---

## Monitoring

### Check Sync Logs in Railway

```bash
# View live logs
railway logs --follow

# Search for errors
railway logs | grep ERROR

# Check specific dataset
railway logs | grep "work_order"
```

### Monitor Row Counts

Run daily to ensure tables aren't bloating:

```sql
SELECT
  'AF_WorkOrder' as table_name,
  COUNT(*) as current_rows,
  (SELECT last_row_count FROM appfolio_sync_state WHERE endpoint = 'work_order') as last_sync_rows
FROM "AF_WorkOrder"
UNION ALL
SELECT
  'AF_TenantDirectory',
  COUNT(*),
  (SELECT last_row_count FROM appfolio_sync_state WHERE endpoint = 'tenant_directory')
FROM "AF_TenantDirectory";
```

**Expected:** Row counts should remain stable (~100-500 per table).

### Check for Failed Syncs

```sql
SELECT *
FROM appfolio_sync_state
WHERE last_run_status = 'failed'
ORDER BY updated_at DESC;
```

---

## Troubleshooting

### Issue: Delta sync not working, always fetching all records

**Cause:** AppFolio Reports API v2 might not support `updated_at_from` for this dataset.

**Solution:**
1. Check Railway logs for API errors
2. If API returns 400/422, that dataset doesn't support delta sync
3. Disable delta for that dataset:

```python
# In jobs/sync_whatever.py
result = sync_details("dataset_name", use_delta=False)
```

4. Or use full replace (truncate + insert):

```sql
-- Add to constants.py
FULL_REPLACE_DATASETS = ["rent_roll", "inspection_detail"]
```

### Issue: Sync state not updating

**Cause:** RPC function call failing.

**Solution:**
1. Check Supabase logs
2. Verify function exists:

```sql
SELECT proname FROM pg_proc WHERE proname = 'update_sync_state';
```

3. Test manually:

```sql
SELECT update_sync_state('test_endpoint', 100, 'success');
SELECT * FROM appfolio_sync_state WHERE endpoint = 'test_endpoint';
```

### Issue: Railway cron not running

**Cause:** Railway free tier might not support cron jobs.

**Solution:**
Use external cron service (cron-job.org) to hit HTTP endpoints.

---

## Testing Delta Sync Support

To test if a specific dataset supports `updated_at_from` filtering:

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

dataset = "work_order"
url = f"{os.getenv('V2_BASE_URL')}/{dataset}"
headers = {
    "Authorization": f"Basic {base64_encoded_credentials}",
    "Content-Type": "application/json"
}

# Test with date filter
response = requests.post(
    url,
    headers=headers,
    json={"updated_at_from": "2026-03-01T00:00:00Z"}
)

if response.status_code == 200:
    print(f"✅ {dataset} supports delta sync")
    print(f"Records returned: {len(response.json()['results'])}")
else:
    print(f"❌ {dataset} does NOT support delta sync")
    print(f"Error: {response.status_code} - {response.text}")
```

---

## Next Steps

1. ✅ **Test locally** - Run each job script and verify delta sync works
2. ⏳ **Push to GitHub** - Commit and push changes
3. ⏳ **Verify Railway deployment** - Check logs after auto-deploy
4. ⏳ **Set up cron jobs** - Configure Railway cron or external service
5. ⏳ **Monitor for 24-48 hours** - Ensure row counts stay stable
6. ⏳ **Test delta filtering** - Create a test change in AppFolio, verify it syncs

---

## Success Criteria

✅ Delta sync working when:
- First run: Fetches all records, stores timestamp
- Second run: Only fetches changed records (0-5 records typically)
- Sync state table updates after each run
- Row counts remain stable (~1,500 total across all AF_ tables)
- Work orders sync every 5 minutes without accumulation

---

## Contact

**Implemented by:** Claude Code
**Date:** March 6, 2026
**Related Migration:** `20260306_appfolio_sync_fix_safe.sql`
**GitHub Repo:** SupabaseAF_appfolo
