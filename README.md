# AppFolio to Supabase Sync Service

Automated sync service that pulls property management data from AppFolio and stores it in Supabase for dashboard applications.

## Quick Start

### Local Development

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env  # Add your credentials

# Run API server
uvicorn app.main:app --reload

# Test sync manually
python -m app.job_runner --dataset work_order
```

### Railway Deployment

The application is deployed on Railway with 4 automated cron services:

| Service | Schedule | Dataset |
|---------|----------|---------|
| Work Orders Sync | Every 5 min (`*/5 * * * *`) | `work_order` |
| Tenants Sync | Hourly (`0 * * * *`) | `tenant_directory` |
| Units Sync | Hourly (`0 * * * *`) | `unit_directory` |
| Properties Sync | Daily (`0 5 * * *`) | `property_group_directory` |

**Branch:** `zeff-delta-sync` (auto-deploys on push)

## Key Features

### Delta Sync System
- Only fetches records changed since last sync
- Prevents database bloat (fixed 329K+ → 802 rows)
- Uses AppFolio's `updated_at_from` filter
- Tracks sync state in database

### Current Status (March 10, 2026)
- ✅ Work Orders: Operational (150 rows)
- ⚠️ Tenants: Blocked (admin access needed)
- ✅ Units: Operational (324 rows)
- ✅ Properties: Operational (66 rows)

**Overall:** 3 of 4 services working (75% operational)

## Project Structure

```
SupabaseAF_appfolo/
├── app/
│   ├── main.py                   # FastAPI application
│   ├── job_runner.py            # Cron job entry point
│   ├── services/
│   │   ├── appfolio.py          # AppFolio API client
│   │   ├── sync.py              # Sync orchestration
│   │   └── supabase_client.py   # Supabase operations
│   └── helpers/
│       ├── constants.py         # Dataset mappings & conflict fields
│       └── utils.py             # Data transformations
├── jobs/                        # Job scripts (legacy)
├── scripts/
│   └── run_audit.py            # Database health check
├── docs/                        # API research & documentation
├── .env                         # Environment variables (local)
└── requirements.txt            # Python dependencies
```

## Environment Variables

Required for both local and Railway deployment:

```bash
SUPABASE_URL=https://wkwmxxlfheywwbgdbzxe.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbG...  # Full JWT token
APPFOLIO_CLIENT_ID=7986fe0a...
APPFOLIO_CLIENT_SECRET=397b9c15...
V1_BASE_URL=https://stantonmgmt.appfolio.com/api/v1
V2_BASE_URL=https://stantonmgmt.appfolio.com/api/v2/reports
```

See `RAILWAY_ENV_VARIABLES.md` for complete reference.

## Key Commands

### Development
```bash
# Start API server
uvicorn app.main:app --reload

# Manual sync (specific dataset)
python -m app.job_runner --dataset work_order

# Database health check
python scripts/run_audit.py
```

### Database Queries

```sql
-- Check sync status
SELECT * FROM appfolio_sync_state ORDER BY last_synced_at DESC;

-- Check row counts
SELECT 'AF_WorkOrder', COUNT(*) FROM "AF_WorkOrder"
UNION ALL SELECT 'AF_TenantDirectory', COUNT(*) FROM "AF_TenantDirectory"
UNION ALL SELECT 'AF_UnitDirectory', COUNT(*) FROM "AF_UnitDirectory"
UNION ALL SELECT 'AF_buildings', COUNT(*) FROM "AF_buildings";
```

## Documentation

| Document | Purpose |
|----------|---------|
| `CLAUDE.md` | Project context for AI assistants |
| `DELTA_SYNC_DEPLOYMENT_GUIDE.md` | Complete deployment & troubleshooting guide |
| `AVAILABLE_AF_TABLES.md` | All 58 available AppFolio tables |
| `AGENTS.md` | Coding guidelines & conventions |
| `RAILWAY_ENV_VARIABLES.md` | Environment variables reference |
| `SESSION_SUMMARY_2026-03-09.md` | Latest implementation session |
| `BUILDINGS_FIX.md` | Historical context for transformation system |

## Common Issues

### Duplicate Key Errors
**Solution:** Ensure `UPSERT_CONFLICT_FIELDS` mapping exists in `app/helpers/constants.py`

### 401 Invalid API Key
**Solution:** Verify Railway environment variables - JWT tokens must be complete (200+ chars)

### AppFolio 429 Rate Limit
**Solution:** Wait 30 minutes between manual sync triggers

### Railway Permission Error
**Solution:** Need admin role for "destructive changes"

## Adding New Tables

1. **Check unique constraint:**
   ```sql
   SELECT conname, a.attname
   FROM pg_constraint c
   JOIN pg_class t ON c.conrelid = t.oid
   JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(c.conkey)
   WHERE t.relname = 'AF_TableName' AND c.contype = 'u';
   ```

2. **Add to `constants.py`:**
   ```python
   UPSERT_CONFLICT_FIELDS = {
       # ... existing
       "new_dataset": "unique_field_name",
   }
   ```

3. **Initialize sync state:**
   ```sql
   INSERT INTO appfolio_sync_state (endpoint, sync_method, last_synced_at, last_run_status, last_row_count)
   VALUES ('new_dataset', 'delta', '1970-01-01T00:00:00Z', 'success', 0);
   ```

4. **Create Railway cron service** with command:
   ```
   python -m app.job_runner --dataset new_dataset
   ```

See `AVAILABLE_AF_TABLES.md` for high-priority table recommendations.

## Success Metrics

**Database Health:**
- Total rows: ~802 (down from 329K+)
- No duplicates
- Growth: <10 rows/day

**Sync Performance:**
- First sync: Fetches all records
- Subsequent syncs: Fetches 0-10 records (delta working)
- All successful syncs show status='success'

## Technology Stack

- **Language:** Python 3.9+
- **Framework:** FastAPI
- **Database:** Supabase (PostgreSQL)
- **API:** AppFolio Reports API v2
- **Deployment:** Railway (Cron Jobs)
- **Version Control:** GitHub

## Repository

**URL:** https://github.com/StantonManagement/SupabaseAF_appfolo

**Active Branch:** `zeff-delta-sync`

**Last Updated:** March 10, 2026
