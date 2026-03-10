# Quick Reference Guide

**Last Updated:** March 10, 2026

## System Status

### Current Services (3/4 Working)
| Service | Status | Last Sync | Records |
|---------|--------|-----------|---------|
| Work Orders | ✅ Operational | March 9, 9:01 AM | 150 |
| Tenants | ⚠️ Blocked | Never (needs admin) | 262 |
| Units | ✅ Operational | March 9, 9:02 AM | 324 |
| Properties | ✅ Operational | March 9, 8:03 AM | 66 |

**Total Database:** 802 rows (99.76% reduction from 329K+)

---

## Quick Commands

### Check Database Health
```bash
python scripts/run_audit.py
```

### Manual Sync (any dataset)
```bash
python -m app.job_runner --dataset work_order
python -m app.job_runner --dataset tenant_directory
python -m app.job_runner --dataset unit_directory
python -m app.job_runner --dataset property_group_directory
```

### Start Local API
```bash
uvicorn app.main:app --reload
```

---

## Railway Service Commands

Each service uses:
```bash
python -m app.job_runner --dataset <dataset_name>
```

**Cron Schedules:**
- Work Orders: `*/5 * * * *` (every 5 min)
- Tenants: `0 * * * *` (hourly)
- Units: `0 * * * *` (hourly)
- Properties: `0 5 * * *` (daily at 5 AM UTC)

---

## Essential SQL Queries

### Check Sync Status
```sql
SELECT endpoint, last_synced_at, last_run_status, last_row_count
FROM appfolio_sync_state
ORDER BY last_synced_at DESC;
```

### Check Row Counts
```sql
SELECT 'AF_WorkOrder' as table_name, COUNT(*) as rows FROM "AF_WorkOrder"
UNION ALL SELECT 'AF_TenantDirectory', COUNT(*) FROM "AF_TenantDirectory"
UNION ALL SELECT 'AF_UnitDirectory', COUNT(*) FROM "AF_UnitDirectory"
UNION ALL SELECT 'AF_buildings', COUNT(*) FROM "AF_buildings";
```

### Check for Duplicates (should be 0)
```sql
SELECT work_order_id, COUNT(*) as count
FROM "AF_WorkOrder"
GROUP BY work_order_id
HAVING COUNT(*) > 1;
```

---

## Environment Variables (Railway)

```bash
SUPABASE_URL=https://wkwmxxlfheywwbgdbzxe.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indrd214eGxmaGV5d3diZ2RienhlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwOTcxOTIsImV4cCI6MjA3OTQ1NzE5Mn0.G4UyeP2BVuGG35oGDXMJcgbSCVVtBhSO6WddG-b6bm4
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indrd214eGxmaGV5d3diZ2RienhlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDA5NzE5MiwiZXhwIjoyMDc5NDU3MTkyfQ.niks8sCfMwsw704YW9fo7CNR9r3JddVCTbxCn-sVyrY
APPFOLIO_CLIENT_ID=7986fe0a73132b6dc3879bbc5d8ee4c8
APPFOLIO_CLIENT_SECRET=397b9c151d85dbe670075dddb8d8e29d
V1_BASE_URL=https://stantonmgmt.appfolio.com/api/v1
V2_BASE_URL=https://stantonmgmt.appfolio.com/api/v2/reports
```

⚠️ No quotes, full JWT tokens (200+ chars)

---

## Dataset Conflict Fields

From `app/helpers/constants.py`:

```python
UPSERT_CONFLICT_FIELDS = {
    "work_order": "work_order_id",
    "tenant_directory": "occupancy_id",
    "unit_directory": "unit_id",
    "property_group_directory": "property_id",
    "buildings": "property_id",
}
```

**Important:** New datasets MUST have conflict field defined to avoid duplicate key errors.

---

## Common Issues & Quick Fixes

| Issue | Quick Fix |
|-------|-----------|
| Duplicate key error | Add conflict field to `UPSERT_CONFLICT_FIELDS` |
| 401 Invalid API key | Check Railway env vars - JWT must be full (200+ chars) |
| 429 Rate limit | Wait 30 min between manual triggers |
| Service not syncing | Check Railway logs, manually trigger "Run now" |
| Wrong dataset | Update Railway start command (needs admin) |

---

## High-Priority Tables to Add

From audit of 58 total AF tables:

1. **AF_Delinquency** (232 rows) - Late payments
2. **AF_TenantLedger** (353 rows) - Financial transactions
3. **AF_RentRoll** (2,636 rows) - Current rent data
4. **AF_VendorDirectory** (429 rows) - Vendor management
5. **AF_GuestCards** (690 rows) - Prospective tenants

See `AVAILABLE_AF_TABLES.md` for complete list.

---

## File Locations

**Key Code:**
- `app/job_runner.py` - Entry point
- `app/services/sync.py` - Sync orchestration
- `app/services/appfolio.py` - API client
- `app/services/supabase_client.py` - Database operations
- `app/helpers/constants.py` - Mappings & conflict fields

**Documentation:**
- `CLAUDE.md` - Project context
- `README.md` - Overview & getting started
- `DELTA_SYNC_DEPLOYMENT_GUIDE.md` - Complete guide
- `AVAILABLE_AF_TABLES.md` - All available tables

---

## Adding New Table (5 Steps)

1. **Check unique constraint** (Supabase SQL Editor)
2. **Add to `UPSERT_CONFLICT_FIELDS`** in `constants.py`
3. **Initialize sync state** (SQL INSERT)
4. **Create Railway cron service** with proper command
5. **Test manually** ("Run now" button)

See `README.md` for detailed steps.

---

## Success Indicators

✅ **Healthy System:**
- Row counts stable (~802 total)
- Sync timestamps updating regularly
- No errors in Railway logs
- Delta sync fetching 0-10 records (not full set)

❌ **Issues:**
- Row counts growing rapidly (>100/hour)
- Sync timestamps stale (>1 day old)
- Errors in Railway logs
- Full syncs every time (not delta)

---

## Emergency Contacts

**Repository:** https://github.com/StantonManagement/SupabaseAF_appfolo

**Branch:** zeff-delta-sync

**Railway:** (Requires access)

**Supabase:** https://supabase.com/dashboard/project/wkwmxxlfheywwbgdbzxe

---

## Next Actions (Current Blockers)

⚠️ **Immediate:**
- [ ] Get Railway admin access to fix Tenants Sync command
- [ ] Test Tenants sync after fix
- [ ] Verify all 4 services showing today's date

✅ **Short Term:**
- [ ] Monitor for 24 hours
- [ ] Consider adding AF_Delinquency table
- [ ] Consider adding AF_RentRoll table

📋 **Medium Term:**
- [ ] Set up automated monitoring
- [ ] Optimize Work Orders frequency (5 min → 15 min?)
- [ ] Document business logic for each table
