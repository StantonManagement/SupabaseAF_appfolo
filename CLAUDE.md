# AppFolio to Supabase Sync - Project Context

**Last Updated:** March 10, 2026
**Status:** ✅ 75% Operational (3 of 4 services working)
**Repository:** SupabaseAF_appfolo
**Branch:** zeff-delta-sync (deployed to Railway)

---

## Project Overview

This project syncs AppFolio property management data to Supabase for use in a management dashboard application. The system uses Railway cron jobs to periodically fetch data from AppFolio's Reports API and upsert it into Supabase PostgreSQL tables.

**Key Achievement:** Fixed massive database bloat issue (329K+ rows → 802 stable rows) by implementing delta sync with timestamp tracking.

---

## Current System Status

### Working Services (3/4) ✅

1. **Work Orders Sync**
   - Schedule: Every 5 minutes (`*/5 * * * *`)
   - Dataset: `work_order` → `AF_WorkOrder`
   - Status: ✅ Operational (last sync: March 9, 2026)
   - Records: 150 rows

2. **Units Sync**
   - Schedule: Hourly (`0 * * * *`)
   - Dataset: `unit_directory` → `AF_UnitDirectory`
   - Status: ✅ Operational (last sync: March 9, 2026 9:02 AM)
   - Records: 324 rows

3. **Properties Sync**
   - Schedule: Daily at 5 AM UTC (`0 5 * * *`)
   - Dataset: `property_group_directory` → `AF_buildings`
   - Status: ✅ Operational (last sync: March 9, 2026 8:03 AM)
   - Records: 66 rows
   - Note: Uses transformation to convert property data to building format

### Blocked Service (1/4) ⚠️

4. **Tenants Sync**
   - Schedule: Hourly (`0 * * * *`)
   - Dataset: `tenant_directory` → `AF_TenantDirectory`
   - Status: ⚠️ BLOCKED - Railway admin access required
   - Issue: Start command incorrectly points to `unit_directory`, needs update to `tenant_directory`
   - Records: 262 rows (not being updated)

---

## Key Technical Fixes (March 9, 2026)

### 1. Upsert ON CONFLICT Bug Fix

**Problem:** Duplicate key constraint violations during upsert
```
duplicate key value violates unique constraint "uq_unit_directory_unit"
```

**Root Cause:** Supabase upsert using default primary key instead of AppFolio-specific unique fields (unit_id, occupancy_id, work_order_id, property_id)

**Solution:** Added explicit ON CONFLICT field mapping

**File:** `app/helpers/constants.py`
```python
UPSERT_CONFLICT_FIELDS = {
    "work_order": "work_order_id",
    "tenant_directory": "occupancy_id",
    "unit_directory": "unit_id",
    "property_group_directory": "property_id",
    "buildings": "property_id",
}
```

**File:** `app/services/supabase_client.py`
```python
conflict_field = UPSERT_CONFLICT_FIELDS.get(dataset)

if conflict_field:
    supabase.table(DETAILS[dataset]).upsert(
        cleaned_record,
        on_conflict=conflict_field
    ).execute()
```

**Commit:** 6a4501f
**Status:** ✅ Fixed and deployed

---

### 2. Sync Status Constraint Fix

**Problem:** Database constraint violation when recording sync status
```
violates check constraint "appfolio_sync_state_last_run_status_check"
```

**Root Cause:** Code using 'partial' status, but database constraint only allows 'success' or 'failed'

**Solution:** Changed status logic

**File:** `app/services/supabase_client.py` (line 125)
```python
# Before:
sync_status = "success" if failed_count == 0 else "partial"

# After:
sync_status = "success" if failed_count == 0 else "failed"
```

**Status:** ✅ Fixed and deployed

---

## Architecture

### System Flow
```
Railway Cron Job
    ↓
job_runner.py (--dataset parameter)
    ↓
sync.py (orchestrates sync)
    ↓
get_last_sync_time() → Supabase RPC
    ↓
appfolio.py (fetch with updated_at_from filter)
    ↓
supabase_client.py (upsert with ON CONFLICT)
    ↓
update_sync_state() → Supabase RPC
```

### Delta Sync Logic

1. Check `appfolio_sync_state` table for last sync timestamp
2. Call AppFolio API with `updated_at_from` parameter (only fetch changed records)
3. Upsert records to Supabase using explicit conflict field
4. Update sync state with new timestamp and row count

**Benefits:**
- Only fetches changed records (0-10 instead of 150+ every time)
- Prevents database bloat
- Reduces API load on AppFolio
- Faster sync times

---

## Database Structure

### Supabase Tables

**Data Tables:**
- `AF_WorkOrder` - Work orders (150 rows, unique: work_order_id)
- `AF_TenantDirectory` - Tenants (262 rows, unique: occupancy_id)
- `AF_UnitDirectory` - Units (324 rows, unique: unit_id)
- `AF_buildings` - Properties (66 rows, unique: property_id)

**System Tables:**
- `appfolio_sync_state` - Tracks last sync timestamp per endpoint
  - Fields: endpoint, last_synced_at, last_run_status, last_row_count, sync_method

**Available but Not Scheduled (54 additional tables):**
- `AF_RentRoll` (2,636 rows) - High priority for future
- `AF_Delinquency` (232 rows) - High priority for future
- `AF_TenantLedger` (353 rows) - High priority for future
- `AF_VendorDirectory` (429 rows) - Medium priority
- `AF_GuestCards` (690 rows) - Medium priority
- See `AVAILABLE_AF_TABLES.md` for complete list

---

## Railway Deployment

### Environment Variables (required for all services)

```bash
SUPABASE_URL=https://wkwmxxlfheywwbgdbzxe.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indrd214eGxmaGV5d3diZ2RienhlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwOTcxOTIsImV4cCI6MjA3OTQ1NzE5Mn0.G4UyeP2BVuGG35oGDXMJcgbSCVVtBhSO6WddG-b6bm4
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indrd214eGxmaGV5d3diZ2RienhlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDA5NzE5MiwiZXhwIjoyMDc5NDU3MTkyfQ.niks8sCfMwsw704YW9fo7CNR9r3JddVCTbxCn-sVyrY
APPFOLIO_CLIENT_ID=7986fe0a73132b6dc3879bbc5d8ee4c8
APPFOLIO_CLIENT_SECRET=397b9c151d85dbe670075dddb8d8e29d
V1_BASE_URL=https://stantonmgmt.appfolio.com/api/v1
V2_BASE_URL=https://stantonmgmt.appfolio.com/api/v2/reports
```

See `RAILWAY_ENV_VARIABLES.md` for reference.

### Service Configuration

**Work Orders Sync:**
- Command: `python -m app.job_runner --dataset work_order`
- Schedule: `*/5 * * * *`

**Tenants Sync:**
- Command: `python -m app.job_runner --dataset tenant_directory` ⚠️ (needs admin to update)
- Schedule: `0 * * * *`

**Units Sync:**
- Command: `python -m app.job_runner --dataset unit_directory`
- Schedule: `0 * * * *`

**Properties Sync:**
- Command: `python -m app.job_runner --dataset property_group_directory`
- Schedule: `0 5 * * *`

---

## Common Issues & Solutions

### Issue 1: Duplicate Key Errors
**Solution:** Ensure `UPSERT_CONFLICT_FIELDS` mapping exists in `constants.py` for the dataset

### Issue 2: 401 Invalid API Key
**Solution:** Check Railway environment variables - JWT tokens must be complete (200+ chars, no quotes)

### Issue 3: AppFolio 429 Rate Limit
**Solution:** Wait 30 minutes between manual "Run now" triggers during testing

### Issue 4: Railway Permission Error
**Solution:** Need admin role to make "destructive changes" (service deletion/recreation)

### Issue 5: Deployment Error "No start command found"
**Solution:** Ensure `jobs/__init__.py` file exists (even if empty) for Python package recognition

---

## Testing & Verification

### Check Database Health
```python
python scripts/run_audit.py
```

### Check Sync State (Supabase SQL Editor)
```sql
SELECT
  endpoint,
  last_synced_at,
  last_run_status,
  last_row_count
FROM appfolio_sync_state
ORDER BY last_synced_at DESC;
```

### Check Row Counts
```sql
SELECT 'AF_WorkOrder', COUNT(*) FROM "AF_WorkOrder"
UNION ALL
SELECT 'AF_TenantDirectory', COUNT(*) FROM "AF_TenantDirectory"
UNION ALL
SELECT 'AF_UnitDirectory', COUNT(*) FROM "AF_UnitDirectory"
UNION ALL
SELECT 'AF_buildings', COUNT(*) FROM "AF_buildings";
```

**Expected:** ~802 total rows, stable over time

---

## Adding New Tables

### High-Priority Candidates
1. `AF_Delinquency` (232 rows) - Late payment tracking
2. `AF_TenantLedger` (353 rows) - Financial transactions
3. `AF_RentRoll` (2,636 rows) - Current rent data

### Steps to Add
1. **Initialize sync state:**
   ```sql
   INSERT INTO appfolio_sync_state (endpoint, sync_method, last_synced_at, last_run_status, last_row_count)
   VALUES ('delinquency', 'delta', '1970-01-01T00:00:00Z', 'success', 0);
   ```

2. **Add conflict field mapping** in `app/helpers/constants.py`:
   ```python
   UPSERT_CONFLICT_FIELDS = {
       # ... existing
       "delinquency": "id",  # Check actual unique constraint
   }
   ```

3. **Create Railway cron service:**
   - Name: Delinquency Sync
   - Command: `python -m app.job_runner --dataset delinquency`
   - Schedule: Daily (`0 0 * * *`)
   - Environment: Copy from `RAILWAY_ENV_VARIABLES.md`

4. **Test:**
   - Manual "Run now" trigger
   - Check logs for success
   - Verify database updated

---

## Current Blockers

### 1. Tenants Sync Configuration ⚠️
- **Issue:** Start command points to wrong dataset (`unit_directory` instead of `tenant_directory`)
- **Impact:** Tenants table not syncing (stuck at 1970-01-01)
- **Blocker:** Railway admin access required to update
- **Workaround:** None - must wait for admin

### 2. AppFolio Rate Limiting (Minor)
- **Issue:** 429 errors if testing too frequently
- **Impact:** Must wait 30 min between manual triggers
- **Workaround:** Wait between tests, or reduce Work Orders frequency to every 15 min

---

## Recent Session History

### March 6, 2026
- Implemented delta sync system
- Created 4 Railway cron services
- Cleaned database (329K → 1.5K rows)

### March 9, 2026
- Fixed upsert ON CONFLICT bug
- Fixed sync status constraint violation
- Successfully tested Units sync (324 records, 0 errors)
- Hit Railway admin permission blocker
- Audited all 58 AF tables
- Created comprehensive documentation

---

## Key Files

### Application Code
- `app/job_runner.py` - Entry point for Railway cron jobs
- `app/services/sync.py` - Delta sync orchestration
- `app/services/appfolio.py` - AppFolio API client
- `app/services/supabase_client.py` - Supabase operations
- `app/helpers/constants.py` - Dataset mappings and conflict fields

### Configuration
- `.env` - Local environment variables (DO NOT commit)
- `RAILWAY_ENV_VARIABLES.md` - Railway environment reference
- `requirements.txt` - Python dependencies

### Documentation
- `CLAUDE.md` (this file) - Project context for AI assistants
- `DELTA_SYNC_DEPLOYMENT_GUIDE.md` - Comprehensive deployment guide
- `AVAILABLE_AF_TABLES.md` - All available AppFolio tables
- `SESSION_SUMMARY_2026-03-09.md` - Latest session summary
- `SESSION_SUMMARY_2026-03-06.md` - Delta sync implementation summary

### Database Scripts
- `initialize_sync_state.sql` - Setup sync state table
- `quick_audit_af_tables.sql` - Fast health check query
- `audit_all_af_tables.sql` - Comprehensive audit
- `scripts/run_audit.py` - Python audit script

### Legacy/Reference
- `AGENTS.md` - Coding guidelines and conventions
- `BUILDINGS_FIX.md` - Historical building transformation fix
- `REPORT_FOR_ALEX.md` - Stakeholder report

---

## Success Metrics

**Database Health:**
- Total rows: ~802 (✅ down from 329K+)
- Growth rate: <10 rows/day (normal operations)
- No duplicates

**Sync Performance:**
- First sync: Fetches all records (150-324 depending on table)
- Subsequent syncs: Fetches 0-10 records (delta working!)
- Sync status: 'success' for all operational services

**System Reliability:**
- 3 of 4 services operational (75%)
- All services auto-deploy on git push
- No errors in Railway logs (except blocked Tenants service)

---

## Next Actions

### Immediate (when admin access granted)
1. Update Tenants Sync start command to `tenant_directory`
2. Test Tenants sync
3. Verify all 4 services showing today's date in sync_state

### Short Term
4. Monitor for 24 hours to ensure stability
5. Consider adding `AF_Delinquency` (high business value)
6. Consider adding `AF_RentRoll` (high business value)

### Medium Term
7. Implement automated monitoring/alerting
8. Add remaining high-priority tables
9. Optimize Work Orders frequency (every 5 min → every 15 min?)
10. Document business logic for each table

---

## Notes for Future Sessions

1. **Always check database state first** - Run `scripts/run_audit.py` to see current status
2. **Watch for rate limiting** - AppFolio returns 429 if syncing too frequently
3. **Admin access required** - Some Railway operations need admin role
4. **Test delta sync** - After adding new table, verify second run fetches 0 records
5. **Unique constraints matter** - Always check table schema before adding to `UPSERT_CONFLICT_FIELDS`

---

**Project Repository:** https://github.com/StantonManagement/SupabaseAF_appfolo
**Branch:** zeff-delta-sync
**Railway Dashboard:** (Requires access)
**Supabase Dashboard:** https://supabase.com/dashboard/project/wkwmxxlfheywwbgdbzxe
