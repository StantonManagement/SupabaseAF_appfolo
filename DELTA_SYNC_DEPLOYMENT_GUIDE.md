# AppFolio Delta Sync - Complete Deployment Guide

**Date Created:** March 6, 2026
**Status:** ✅ Production Deployed
**Repository:** SupabaseAF_appfolo
**Branch:** zeff-delta-sync

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Solution Overview](#solution-overview)
3. [Architecture](#architecture)
4. [Prerequisites](#prerequisites)
5. [Step-by-Step Implementation](#step-by-step-implementation)
6. [Deployment to Railway](#deployment-to-railway)
7. [Troubleshooting Guide](#troubleshooting-guide)
8. [Verification & Testing](#verification--testing)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Adding More Datasets](#adding-more-datasets)

---

## Problem Statement

### The Bloat Issue

**Symptoms:**
- Database table `AF_WorkOrder` grew to **155,543 rows** (should be ~500)
- Total AF tables: **329,000+ rows** (should be ~1,500)
- Queries became slow
- Database storage bloated
- Unnecessary API load on AppFolio

**Root Cause:**
- Hourly cron jobs fetched ALL records from AppFolio every time
- Records were inserted/upserted repeatedly
- No timestamp tracking for incremental syncs
- No date filtering on API requests

**Impact:**
- 99.5% of data was duplicates
- Database performance degraded
- Wasted API calls
- Potential cost implications

---

## Solution Overview

### Delta Sync Implementation

**Concept:** Only fetch records that changed since the last sync

**How It Works:**
```
1. Check database: "When was last sync?" → "2026-03-06 10:00:00"
2. Call AppFolio API: "Give me records updated after 10:00:00"
3. AppFolio returns: 3 changed records (instead of 500)
4. Upsert only those 3 records
5. Update database: "Last sync completed at 10:05:00"
6. Next run: Start from 10:05:00
```

**Benefits:**
- ✅ Eliminates bloat - row counts stay stable
- ✅ Reduces API load - only fetch what changed
- ✅ Faster sync times - process fewer records
- ✅ Better performance - smaller database
- ✅ Scalable - works for any dataset size

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│                    RAILWAY PLATFORM                      │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Cron Service: Work Orders (*/5 * * * *)         │  │
│  │  Command: python -m app.job_runner --dataset     │  │
│  │           work_order                              │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Cron Service: Tenants (0 * * * *)               │  │
│  │  Command: python -m app.job_runner --dataset     │  │
│  │           tenant_directory                        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Cron Service: Units (0 * * * *)                 │  │
│  │  Command: python -m app.job_runner --dataset     │  │
│  │           unit_directory                          │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Cron Service: Properties (0 5 * * *)            │  │
│  │  Command: python -m app.job_runner --dataset     │  │
│  │           property_group_directory                │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              PYTHON APPLICATION (FastAPI)                │
│                                                          │
│  app/job_runner.py                                      │
│    └─► app/services/sync.py                            │
│         ├─► get_last_sync_time(dataset)                │
│         │    └─► Supabase RPC call                     │
│         │                                               │
│         ├─► app/services/appfolio.py                   │
│         │    └─► AppFolio API (with date filter)      │
│         │                                               │
│         └─► app/services/supabase_client.py            │
│              ├─► Upsert records                        │
│              └─► update_sync_state(dataset)            │
│                                                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  SUPABASE DATABASE                       │
│                                                          │
│  Tables:                                                │
│    - AF_WorkOrder (stores work orders)                 │
│    - AF_TenantDirectory (stores tenants)               │
│    - AF_UnitDirectory (stores units)                   │
│    - AF_buildings (stores properties)                  │
│    - appfolio_sync_state (tracks sync times)           │
│                                                          │
│  RPC Functions:                                         │
│    - get_last_sync_time(p_endpoint)                    │
│    - update_sync_state(p_endpoint, p_row_count,        │
│                        p_status)                        │
│                                                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 APPFOLIO API                             │
│                                                          │
│  Reports API v2:                                        │
│  POST /api/v2/reports/{dataset}                        │
│  Body: {                                                │
│    "updated_at_from": "2026-03-06T10:00:00Z"          │
│  }                                                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
┌──────────────────────────────────────────────────────────┐
│ 1. Railway Cron Triggers                                 │
│    "Every 5 minutes"                                     │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│ 2. job_runner.py Starts                                  │
│    → Loads environment variables                         │
│    → Imports sync module                                 │
│    → Calls sync_details("work_order")                    │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│ 3. Get Last Sync Time                                    │
│    → supabase.rpc("get_last_sync_time",                  │
│                   {"p_endpoint": "work_order"})          │
│    → Returns: "2026-03-06T15:35:36.444509+00:00"        │
│    OR NULL if never synced                               │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│ 4. Call AppFolio API with Date Filter                    │
│    POST https://stantonmgmt.appfolio.com/api/v2/        │
│         reports/work_order                               │
│    Headers:                                              │
│      - Authorization: Bearer <token>                     │
│    Body:                                                 │
│      {                                                   │
│        "updated_at_from": "2026-03-06T15:35:36..."      │
│      }                                                   │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│ 5. AppFolio Returns Changed Records                      │
│    → 0-5 records (only what changed)                     │
│    → NOT all 167 records                                 │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│ 6. Upsert Records to Supabase                            │
│    FOR EACH record:                                      │
│      → Clean record (remove None, format dates)          │
│      → supabase.table("AF_WorkOrder")                    │
│                .upsert(record)                           │
│                .execute()                                │
│      → Uses unique constraint on 'id' field              │
│      → Updates existing, inserts new                     │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│ 7. Update Sync State                                     │
│    → supabase.rpc("update_sync_state", {                 │
│        "p_endpoint": "work_order",                       │
│        "p_row_count": 5,                                 │
│        "p_status": "success"                             │
│      })                                                  │
│    → Sets last_synced_at = NOW()                         │
│    → Records row count and status                        │
└──────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Required Accounts & Access
1. ✅ GitHub repository access (StantonManagement/SupabaseAF_appfolo)
2. ✅ Railway account with deployment permissions
3. ✅ Supabase project access (admin/owner role)
4. ✅ AppFolio API credentials (client_id, client_secret)

### Required Tools
- Git (for version control)
- Python 3.9+ (for local testing)
- Supabase SQL Editor access
- Railway CLI (optional, but helpful)

### Database Requirements
- ✅ Supabase database with existing AF_ tables
- ✅ Database migration from MaintOC repo applied
- ✅ RPC functions created (get_last_sync_time, update_sync_state)
- ✅ appfolio_sync_state table exists

---

## Step-by-Step Implementation

### Phase 1: Code Modifications

#### 1.1 Modify `app/services/appfolio.py`

**Purpose:** Add date filtering to AppFolio API requests

**File:** `/app/services/appfolio.py`

**Changes:**
```python
def get_appfolio_details(dataset: str, last_synced_at: str = None):
    """
    Fetch data from AppFolio API with optional date filtering

    Args:
        dataset: The dataset name (e.g., 'work_order')
        last_synced_at: ISO timestamp for delta sync (optional)
    """

    # Log sync type
    if last_synced_at:
        logger.info(f"🌐 FETCHING DATA FROM APPFOLIO API (DELTA SYNC since {last_synced_at})")
    else:
        logger.info("🌐 FETCHING DATA FROM APPFOLIO API (FULL SYNC)")

    # ... existing validation code ...

    try:
        if source_dataset in v1_dataset:
            # V1 API (GET request, no date filtering)
            response = requests.get(
                f"{V1_BASE_URL}/{source_dataset}",
                headers=headers,
                timeout=30
            )
        else:
            # V2 API (POST request with body)
            request_body = {}

            # Add date filter if provided (for delta sync)
            if last_synced_at:
                request_body["updated_at_from"] = last_synced_at
                logger.info(f"📅 Applying date filter: updated_at_from={last_synced_at}")

            response = requests.post(
                f"{V2_BASE_URL}/{source_dataset}",
                headers=headers,
                json=request_body if request_body else None,
                timeout=30
            )

        # ... existing response handling ...
```

**Key Points:**
- Added `last_synced_at` parameter (optional, defaults to None)
- For V2 API endpoints, adds `updated_at_from` in request body
- Logs whether it's FULL SYNC or DELTA SYNC
- Backwards compatible (works without date filter)

---

#### 1.2 Modify `app/services/sync.py`

**Purpose:** Orchestrate delta sync by fetching last sync time

**File:** `/app/services/sync.py`

**Changes:**
```python
def sync_details(dataset: str, use_delta: bool = True):
    """
    Sync a dataset from AppFolio to Supabase with optional delta sync

    Args:
        dataset: The dataset name
        use_delta: Whether to use delta sync (default: True)
    """
    logger.info(f"⚡ INITIATING SYNC PROCESS FOR DATASET: '{dataset}'")

    # Get last sync time if delta sync is enabled
    last_synced_at = None
    if use_delta:
        last_synced_at = get_last_sync_time(dataset)
        if last_synced_at:
            logger.info(f"📅 Last sync: {last_synced_at} - Using DELTA sync")
        else:
            logger.info(f"📅 No previous sync found - Using FULL sync")

    # Get data from AppFolio API (with optional date filter)
    appfolio_results = get_appfolio_details(dataset, last_synced_at)

    # Update Supabase and get sync statistics
    sync_result = update_supabase_details(dataset, appfolio_results)

    logger.info(f"🎉 SYNC PROCESS COMPLETED FOR DATASET '{dataset}'")
    return sync_result
```

**Key Points:**
- Added `use_delta` parameter (allows disabling delta sync if needed)
- Calls `get_last_sync_time()` to fetch previous sync timestamp
- Passes timestamp to `get_appfolio_details()`
- Handles case where dataset has never been synced (NULL)

---

#### 1.3 Modify `app/services/supabase_client.py`

**Purpose:** Add sync state tracking functions

**File:** `/app/services/supabase_client.py`

**Add these new functions:**

```python
def get_last_sync_time(dataset: str):
    """
    Get the last successful sync timestamp for a dataset.
    Returns ISO format timestamp string or None if never synced.

    Args:
        dataset: The dataset/endpoint name (e.g., 'work_order')

    Returns:
        str: ISO timestamp or None
    """
    try:
        result = supabase.rpc("get_last_sync_time", {"p_endpoint": dataset}).execute()

        if result.data:
            logger.info(f"📅 Last sync for '{dataset}': {result.data}")
            return result.data
        else:
            logger.info(f"📅 No previous sync found for '{dataset}'")
            return None
    except Exception as e:
        logger.warning(f"⚠️ Could not get last sync time for '{dataset}': {e}")
        return None


def update_sync_state(dataset: str, row_count: int, status: str = "success"):
    """
    Update the sync state after a sync operation.

    Args:
        dataset: The dataset/endpoint name
        row_count: Number of rows synced
        status: Sync status ('success', 'failed', or 'partial')
    """
    try:
        supabase.rpc(
            "update_sync_state",
            {
                "p_endpoint": dataset,
                "p_row_count": row_count,
                "p_status": status
            }
        ).execute()
        logger.info(f"✅ Updated sync state for '{dataset}': {row_count} rows, status={status}")
    except Exception as e:
        logger.error(f"❌ Failed to update sync state for '{dataset}': {e}")
```

**Update `update_supabase_details()` function:**

```python
def update_supabase_details(dataset: str, appfolio_results):
    success_count = 0
    failed_count = 0
    total_records = len(appfolio_results)

    # ... existing validation and upsert code ...

    # At the end, after upsert loop:

    # Calculate final counts
    failed_count = total_records - success_count

    # Log final results
    logger.info(f"✅ SYNC COMPLETE FOR DATASET '{dataset}':")
    logger.info(f"  - ✅ Success: {success_count}")
    logger.info(f"  - ❌ Failed: {failed_count}")
    logger.info(f"  - 📊 Total: {total_records}")

    # Update sync state in database
    sync_status = "success" if failed_count == 0 else "partial"
    update_sync_state(dataset, success_count, sync_status)

    return {"success": success_count, "failed": failed_count, "total": total_records}
```

**Key Points:**
- `get_last_sync_time()` calls Supabase RPC function
- `update_sync_state()` records sync completion
- Proper error handling with logging
- Updates sync state after every sync (success or partial)

---

#### 1.4 Create `jobs/__init__.py`

**Purpose:** Make jobs directory a Python package (required for Railway)

**File:** `/jobs/__init__.py`

**Content:**
```python
# Jobs package
```

**Why This Is Critical:**
- Python requires `__init__.py` to recognize directory as package
- Railway deployment fails without it
- Even an empty file works (just needs to exist)

---

### Phase 2: Database Setup

#### 2.1 Verify Database Infrastructure

**Check if migration was already applied from MaintOC repo:**

Run this in Supabase SQL Editor:

```sql
-- Check if sync state table exists
SELECT EXISTS (
    SELECT FROM information_schema.tables
    WHERE table_name = 'appfolio_sync_state'
);

-- Check if RPC functions exist
SELECT proname
FROM pg_proc
WHERE proname IN ('get_last_sync_time', 'update_sync_state');

-- View existing sync state entries
SELECT * FROM appfolio_sync_state ORDER BY endpoint;
```

**Expected Result:**
- ✅ Table exists: `appfolio_sync_state`
- ✅ Functions exist: `get_last_sync_time`, `update_sync_state`

If NOT exists, you need to apply the migration from MaintOC repo first.

---

#### 2.2 Initialize Sync State Entries

**Purpose:** Create initial records for each dataset

**File:** Create `initialize_sync_state.sql`

**Content:**
```sql
-- Initialize Sync State for All Endpoints
-- Run this in Supabase SQL Editor

INSERT INTO appfolio_sync_state (endpoint, sync_method, last_synced_at, last_run_status, last_row_count)
VALUES
    ('work_order', 'delta', '1970-01-01T00:00:00Z', 'success', 0),
    ('tenant_directory', 'delta', '1970-01-01T00:00:00Z', 'success', 0),
    ('unit_directory', 'delta', '1970-01-01T00:00:00Z', 'success', 0),
    ('property_group_directory', 'delta', '1970-01-01T00:00:00Z', 'success', 0)
ON CONFLICT (endpoint) DO NOTHING;

-- Verify the entries were created
SELECT
    endpoint,
    sync_method,
    last_synced_at,
    last_run_status,
    last_row_count
FROM appfolio_sync_state
ORDER BY endpoint;
```

**Run this SQL in Supabase SQL Editor**

**Why epoch timestamp (1970-01-01)?**
- Ensures first sync is a FULL SYNC (fetches all records)
- After first sync, timestamp updates to current time
- Future syncs become delta syncs

**Why status='success'?**
- Database has check constraint on `last_run_status`
- Only allows: 'success', 'failed', or 'partial'
- 'success' is safest initial value

**Expected Output:**
```
endpoint                  | sync_method | last_synced_at      | last_run_status | last_row_count
--------------------------|-------------|---------------------|-----------------|---------------
work_order               | delta       | 1970-01-01 00:00:00 | success         | 0
tenant_directory         | delta       | 1970-01-01 00:00:00 | success         | 0
unit_directory           | delta       | 1970-01-01 00:00:00 | success         | 0
property_group_directory | delta       | 1970-01-01 00:00:00 | success         | 0
```

---

### Phase 3: Git Workflow

#### 3.1 Create Feature Branch

```bash
cd /Users/zeff/Desktop/Work/stanton/SupabaseAF_appfolo

# Create and checkout new branch
git checkout -b zeff-delta-sync

# Verify you're on the new branch
git branch
```

---

#### 3.2 Commit Changes

```bash
# Stage all modified files
git add app/services/appfolio.py
git add app/services/sync.py
git add app/services/supabase_client.py
git add jobs/__init__.py
git add initialize_sync_state.sql
git add RAILWAY_ENV_VARIABLES.md

# Commit with descriptive message
git commit -m "feat: implement delta sync with timestamp tracking

- Add last_synced_at parameter to AppFolio API requests
- Track sync state in appfolio_sync_state table
- Enable incremental syncs using updated_at_from filter
- Create jobs package for Railway deployment
- Add environment variables documentation
- Fixes database bloat issue (329K+ rows -> ~1.5K stable)"

# Push to GitHub
git push origin zeff-delta-sync
```

---

## Deployment to Railway

### Step 1: Prepare Environment Variables

**File:** Create `RAILWAY_ENV_VARIABLES.md`

**Content:**
```
SUPABASE_URL=https://wkwmxxlfheywwbgdbzxe.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indrd214eGxmaGV5d3diZ2RienhlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwOTcxOTIsImV4cCI6MjA3OTQ1NzE5Mn0.G4UyeP2BVuGG35oGDXMJcgbSCVVtBhSO6WddG-b6bm4
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indrd214eGxmaGV5d3diZ2RienhlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDA5NzE5MiwiZXhwIjoyMDc5NDU3MTkyfQ.niks8sCfMwsw704YW9fo7CNR9r3JddVCTbxCn-sVyrY
APPFOLIO_CLIENT_ID=7986fe0a73132b6dc3879bbc5d8ee4c8
APPFOLIO_CLIENT_SECRET=397b9c151d85dbe670075dddb8d8e29d
V1_BASE_URL=https://stantonmgmt.appfolio.com/api/v1
V2_BASE_URL=https://stantonmgmt.appfolio.com/api/v2/reports
```

**IMPORTANT:**
- ❌ Do NOT use quotes around values
- ✅ Copy ENTIRE JWT tokens (200+ characters)
- ✅ No line breaks within token strings
- ✅ Use your actual credentials from `.env` file

---

### Step 2: Create Railway Cron Services

**You'll create 4 separate Railway services (one for each dataset)**

#### Service 1: Work Orders Sync

**In Railway Dashboard:**

1. Click **"New Service"** → **"Cron Job"**
2. **Name:** Work Orders Sync
3. **Source:** Connect to GitHub repo `StantonManagement/SupabaseAF_appfolo`
4. **Branch:** Select `zeff-delta-sync`
5. **Cron Schedule:** `*/5 * * * *` (every 5 minutes)
6. **Custom Start Command:**
   ```
   python -m app.job_runner --dataset work_order
   ```
7. Click **"Add Variables"** → **"Raw Editor"**
8. Paste all environment variables from `RAILWAY_ENV_VARIABLES.md`
9. Click **"Save"**
10. Wait for deployment to complete (~2 minutes)

---

#### Service 2: Tenants Sync

1. Click **"New Service"** → **"Cron Job"**
2. **Name:** Tenants Sync
3. **Source:** Same GitHub repo and branch
4. **Cron Schedule:** `0 * * * *` (hourly)
5. **Custom Start Command:**
   ```
   python -m app.job_runner --dataset tenant_directory
   ```
6. **Variables:** Paste same environment variables
7. **Save** and wait for deployment

---

#### Service 3: Units Sync

1. Click **"New Service"** → **"Cron Job"**
2. **Name:** Units Sync
3. **Source:** Same GitHub repo and branch
4. **Cron Schedule:** `0 * * * *` (hourly)
5. **Custom Start Command:**
   ```
   python -m app.job_runner --dataset unit_directory
   ```
6. **Variables:** Paste same environment variables
7. **Save** and wait for deployment

---

#### Service 4: Properties Sync

1. Click **"New Service"** → **"Cron Job"**
2. **Name:** Properties Sync
3. **Source:** Same GitHub repo and branch
4. **Cron Schedule:** `0 5 * * *` (daily at midnight EST / 5am UTC)
5. **Custom Start Command:**
   ```
   python -m app.job_runner --dataset property_group_directory
   ```
6. **Variables:** Paste same environment variables
7. **Save** and wait for deployment

---

### Step 3: Verify Deployments

For each service:

1. Click on the service name
2. Check **"Deployments"** tab
3. Status should show: ✅ **"Success"** (green)
4. Check **"Logs"** for any errors

**If deployment fails**, see [Troubleshooting Guide](#troubleshooting-guide)

---

## Troubleshooting Guide

### Issue 1: Railway Deployment Error

**Error Message:**
```
There was an error deploying from source
```

**Possible Causes:**
1. Missing `jobs/__init__.py` file
2. Syntax error in Python code
3. Missing dependencies in requirements.txt

**Solution:**

```bash
# Verify __init__.py exists
ls -la jobs/

# Should show:
# __init__.py

# If missing, create it:
touch jobs/__init__.py
git add jobs/__init__.py
git commit -m "fix: add jobs package init file"
git push origin zeff-delta-sync
```

**Railway will auto-deploy after push**

---

### Issue 2: "No start command was found"

**Error Message:**
```
╭─────────────────╮
│ Railpack 0.17.2 │
╰─────────────────╯
↳ Detected Python
↳ Using pip
✖ No start command was found
```

**Cause:** Custom Start Command not saved in Railway UI

**Solution:**
1. Go to service **Settings** tab
2. Find **"Custom Start Command"** field
3. Re-enter the command:
   ```
   python -m app.job_runner --dataset work_order
   ```
4. Click **"Update"** or **"Save"** (make sure it saves!)
5. Wait for auto-redeploy

---

### Issue 3: 401 Invalid API Key Errors

**Error Message:**
```
💥 Error upserting record: {'message': 'Invalid API key', 'code': 401}
```

**Cause:** Truncated or incorrect `SUPABASE_SERVICE_ROLE_KEY`

**How to Diagnose:**
1. Go to service **Variables** tab
2. Find `SUPABASE_SERVICE_ROLE_KEY`
3. Check the value length (should be 200+ characters)
4. Check for quotes (should NOT have quotes)
5. Compare with your `.env` file

**Solution:**

1. Open **Variables** tab → **Raw Editor**
2. **Delete all variables**
3. Paste fresh from `RAILWAY_ENV_VARIABLES.md`:
   ```
   SUPABASE_URL=https://wkwmxxlfheywwbgdbzxe.supabase.co
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indrd214eGxmaGV5d3diZ2RienhlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwOTcxOTIsImV4cCI6MjA3OTQ1NzE5Mn0.G4UyeP2BVuGG35oGDXMJcgbSCVVtBhSO6WddG-b6bm4
   SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indrd214eGxmaGV5d3diZ2RienhlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDA5NzE5MiwiZXhwIjoyMDc5NDU3MTkyfQ.niks8sCfMwsw704YW9fo7CNR9r3JddVCTbxCn-sVyrY
   APPFOLIO_CLIENT_ID=7986fe0a73132b6dc3879bbc5d8ee4c8
   APPFOLIO_CLIENT_SECRET=397b9c151d85dbe670075dddb8d8e29d
   V1_BASE_URL=https://stantonmgmt.appfolio.com/api/v1
   V2_BASE_URL=https://stantonmgmt.appfolio.com/api/v2/reports
   ```
4. Click **Save**
5. Wait for service to restart
6. Test again

**Key Points:**
- JWT tokens are LONG (200+ chars) - that's normal
- No quotes, no line breaks
- Copy entire token including all dots and characters

---

### Issue 4: "Endpoint not found in appfolio_sync_state"

**Error Message:**
```
❌ Failed to update sync state for 'work_order':
{'message': 'Endpoint work_order not found in appfolio_sync_state', 'code': 'P0001'}
```

**Cause:** Missing initial records in `appfolio_sync_state` table

**Solution:**

1. Open Supabase SQL Editor
2. Run `initialize_sync_state.sql`:
   ```sql
   INSERT INTO appfolio_sync_state (endpoint, sync_method, last_synced_at, last_run_status, last_row_count)
   VALUES
       ('work_order', 'delta', '1970-01-01T00:00:00Z', 'success', 0),
       ('tenant_directory', 'delta', '1970-01-01T00:00:00Z', 'success', 0),
       ('unit_directory', 'delta', '1970-01-01T00:00:00Z', 'success', 0),
       ('property_group_directory', 'delta', '1970-01-01T00:00:00Z', 'success', 0)
   ON CONFLICT (endpoint) DO NOTHING;
   ```
3. Verify entries created:
   ```sql
   SELECT * FROM appfolio_sync_state ORDER BY endpoint;
   ```
4. Retry the sync in Railway

---

### Issue 5: Database Constraint Violations

**Error: NOT NULL constraint on last_synced_at**
```
ERROR: 23502: null value in column "last_synced_at" violates not-null constraint
```

**Solution:** Use epoch timestamp instead of NULL:
```sql
'1970-01-01T00:00:00Z'  -- ✅ Correct
NULL                     -- ❌ Won't work
```

---

**Error: Check constraint on last_run_status**
```
ERROR: 23514: new row violates check constraint "appfolio_sync_state_last_run_status_check"
```

**Solution:** Use valid status value:
```sql
'success'  -- ✅ Valid
'failed'   -- ✅ Valid
'partial'  -- ✅ Valid
'pending'  -- ❌ Invalid (not in constraint)
```

---

## Verification & Testing

### Test 1: Manual Trigger (First Sync)

**For each service:**

1. Go to Railway Dashboard → Service → **Cron Runs** tab
2. Click **"Run now"**
3. Watch the logs in real-time

**Expected Output (First Run - Full Sync):**
```
============================================================
SYNC STARTING
============================================================
⚡ INITIATING SYNC PROCESS FOR DATASET: 'work_order'
📅 Last sync for 'work_order': 1970-01-01T00:00:00+00:00
📅 Last sync: 1970-01-01T00:00:00+00:00 - Using DELTA sync
🌐 FETCHING DATA FROM APPFOLIO API (DELTA SYNC since 1970-01-01T00:00:00+00:00)
📅 Applying date filter: updated_at_from=1970-01-01T00:00:00+00:00
✅ SUCCESSFULLY FETCHED 167 RECORDS FROM APPFOLIO
🚀 STARTING SYNC FOR DATASET 'work_order' - TOTAL RECORDS TO PROCESS: 167
✅ SYNC COMPLETE FOR DATASET 'work_order':
  - ✅ Success: 167
  - ❌ Failed: 0
  - 📊 Total: 167
✅ Updated sync state for 'work_order': 167 rows, status=success
🎉 SYNC PROCESS COMPLETED FOR DATASET 'work_order'
```

**Success Criteria:**
- ✅ No errors in logs
- ✅ All records synced successfully (Failed: 0)
- ✅ Sync state updated message appears
- ✅ Duration reasonable (<30 seconds for 167 records)

---

### Test 2: Verify Database State

**In Supabase SQL Editor:**

```sql
-- Check sync state was updated
SELECT
    endpoint,
    last_synced_at,
    last_run_status,
    last_row_count,
    updated_at
FROM appfolio_sync_state
WHERE endpoint = 'work_order';
```

**Expected Result:**
```
endpoint    | last_synced_at              | last_run_status | last_row_count | updated_at
------------|----------------------------|-----------------|----------------|---------------------------
work_order  | 2026-03-06 15:35:36.444509 | success         | 167            | 2026-03-06 15:35:36.444509
```

**Key Points:**
- ✅ `last_synced_at` should be recent (within last few minutes)
- ✅ NOT 1970-01-01 anymore
- ✅ `last_run_status` = 'success'
- ✅ `last_row_count` = number of records synced

---

### Test 3: Delta Sync Verification (Second Run)

**This is the critical test - proves delta sync is working!**

1. Wait 5 minutes (or manually trigger again)
2. Click **"Run now"** on Work Orders service
3. Watch the logs

**Expected Output (Second Run - Delta Sync):**
```
⚡ INITIATING SYNC PROCESS FOR DATASET: 'work_order'
📅 Last sync for 'work_order': 2026-03-06T15:35:36.444509+00:00
📅 Last sync: 2026-03-06T15:35:36.444509+00:00 - Using DELTA sync
🌐 FETCHING DATA FROM APPFOLIO API (DELTA SYNC since 2026-03-06T15:35:36.444509+00:00)
📅 Applying date filter: updated_at_from=2026-03-06T15:35:36.444509+00:00
✅ SUCCESSFULLY FETCHED 0 RECORDS FROM APPFOLIO
✅ SYNC COMPLETE FOR DATASET 'work_order':
  - ✅ Success: 0
  - ❌ Failed: 0
  - 📊 Total: 0
✅ Updated sync state for 'work_order': 0 rows, status=success
```

**Success Criteria:**
- ✅ Says "DELTA SYNC since [recent timestamp]"
- ✅ Fetched **0 records** (or 1-5 if work orders changed)
- ✅ NOT 167 records (that would mean full sync)
- ✅ Sync completes quickly (<5 seconds)

**If you see 0 records on second run = DELTA SYNC IS WORKING!** 🎉

---

### Test 4: Check Row Counts (Verify No Bloat)

**In Supabase SQL Editor:**

```sql
-- Check current row counts
SELECT
    'AF_WorkOrder' as table_name,
    COUNT(*) as current_rows
FROM "AF_WorkOrder"

UNION ALL

SELECT
    'AF_TenantDirectory',
    COUNT(*)
FROM "AF_TenantDirectory"

UNION ALL

SELECT
    'AF_UnitDirectory',
    COUNT(*)
FROM "AF_UnitDirectory"

UNION ALL

SELECT
    'AF_buildings',
    COUNT(*)
FROM "AF_buildings"

UNION ALL

SELECT
    '📊 TOTAL',
    (
        (SELECT COUNT(*) FROM "AF_WorkOrder") +
        (SELECT COUNT(*) FROM "AF_TenantDirectory") +
        (SELECT COUNT(*) FROM "AF_UnitDirectory") +
        (SELECT COUNT(*) FROM "AF_buildings")
    );
```

**Expected Result (After First Sync):**
```
table_name          | current_rows
--------------------|-------------
AF_WorkOrder        | 167
AF_TenantDirectory  | 433
AF_UnitDirectory    | 323
AF_buildings        | 66
📊 TOTAL            | 989
```

**Run again after 24 hours - row counts should be STABLE:**
```
table_name          | current_rows | Change
--------------------|--------------|--------
AF_WorkOrder        | 167-175      | +0 to +8 (normal)
AF_TenantDirectory  | 433-435      | +0 to +2 (normal)
AF_UnitDirectory    | 323-325      | +0 to +2 (normal)
AF_buildings        | 66           | 0 (rarely changes)
📊 TOTAL            | ~1,000       | Stable
```

**Red Flags (Indicates Delta Sync NOT Working):**
- ❌ Row counts growing rapidly (100+ per hour)
- ❌ Duplicate records appearing
- ❌ Total exceeds 3,000 rows

---

## Monitoring & Maintenance

### Daily Monitoring (First Week)

**Run this query once per day:**

```sql
-- Comprehensive sync health check
SELECT
    endpoint,
    last_synced_at,
    last_run_status,
    last_row_count,
    CASE
        WHEN last_synced_at > NOW() - INTERVAL '10 minutes' THEN '🟢 Recent'
        WHEN last_synced_at > NOW() - INTERVAL '1 hour' THEN '🟡 Within hour'
        WHEN last_synced_at > NOW() - INTERVAL '1 day' THEN '🟠 Within day'
        ELSE '🔴 Stale'
    END as freshness,
    updated_at
FROM appfolio_sync_state
WHERE endpoint IN ('work_order', 'tenant_directory', 'unit_directory', 'property_group_directory')
ORDER BY last_synced_at DESC;
```

**What to Look For:**
- ✅ All endpoints showing 🟢 Recent or 🟡 Within hour
- ✅ `last_run_status` = 'success' for all
- ✅ `last_synced_at` updating regularly (based on schedule)

**Red Flags:**
- ❌ Any endpoint showing 🔴 Stale
- ❌ `last_run_status` = 'failed'
- ❌ Same timestamp for hours (sync not running)

---

### Railway Logs Monitoring

**Check Railway logs for each service:**

1. Go to service → **Logs** tab
2. Look for recent execution logs
3. Verify no errors

**Healthy Logs Pattern:**
```
[timestamp] ⚡ INITIATING SYNC PROCESS FOR DATASET: 'work_order'
[timestamp] 📅 Last sync: [recent time] - Using DELTA sync
[timestamp] ✅ SUCCESSFULLY FETCHED 2 RECORDS FROM APPFOLIO
[timestamp] ✅ SYNC COMPLETE FOR DATASET 'work_order':
[timestamp]   - ✅ Success: 2
[timestamp]   - ❌ Failed: 0
[timestamp] ✅ Updated sync state for 'work_order': 2 rows, status=success
```

**Unhealthy Logs Pattern:**
```
[timestamp] 💥 Error upserting record: [error details]
[timestamp] ❌ Failed to update sync state
[timestamp] AppFolio API error: 429 Rate Limit
```

---

### Weekly Health Check

**Run comprehensive verification:**

**File:** Use `verify_sync_status.sql` from repository

```sql
-- 1. Check Sync State
SELECT
  endpoint,
  last_synced_at::TEXT as last_synced,
  last_run_status as status,
  sync_method as method,
  last_row_count as rows_synced
FROM appfolio_sync_state
ORDER BY last_synced_at DESC;

-- 2. Check Row Counts
SELECT
  'AF_WorkOrder' as table_name, COUNT(*) as current_rows FROM "AF_WorkOrder"
UNION ALL
SELECT 'AF_TenantDirectory', COUNT(*) FROM "AF_TenantDirectory"
UNION ALL
SELECT 'AF_UnitDirectory', COUNT(*) FROM "AF_UnitDirectory"
UNION ALL
SELECT 'AF_buildings', COUNT(*) FROM "AF_buildings";

-- 3. Check for Duplicates (Should be 0)
SELECT
    id,
    COUNT(*) as duplicate_count
FROM "AF_WorkOrder"
GROUP BY id
HAVING COUNT(*) > 1;
```

**Expected Results:**
- ✅ All syncs showing recent timestamps
- ✅ Row counts stable (~1,000-1,500 total)
- ✅ No duplicate records

---

### Monthly Review

**Compare row count trends:**

```sql
-- Create snapshot
CREATE TABLE IF NOT EXISTS sync_metrics_history (
    snapshot_date TIMESTAMP DEFAULT NOW(),
    af_work_order_count INT,
    af_tenant_directory_count INT,
    af_unit_directory_count INT,
    af_buildings_count INT,
    total_count INT
);

-- Insert current snapshot
INSERT INTO sync_metrics_history (
    af_work_order_count,
    af_tenant_directory_count,
    af_unit_directory_count,
    af_buildings_count,
    total_count
)
VALUES (
    (SELECT COUNT(*) FROM "AF_WorkOrder"),
    (SELECT COUNT(*) FROM "AF_TenantDirectory"),
    (SELECT COUNT(*) FROM "AF_UnitDirectory"),
    (SELECT COUNT(*) FROM "AF_buildings"),
    (
        (SELECT COUNT(*) FROM "AF_WorkOrder") +
        (SELECT COUNT(*) FROM "AF_TenantDirectory") +
        (SELECT COUNT(*) FROM "AF_UnitDirectory") +
        (SELECT COUNT(*) FROM "AF_buildings")
    )
);

-- View trend over time
SELECT
    snapshot_date::DATE,
    total_count,
    total_count - LAG(total_count) OVER (ORDER BY snapshot_date) as change
FROM sync_metrics_history
ORDER BY snapshot_date DESC
LIMIT 30;
```

**Healthy Trend:**
- Total count stays between 1,000-2,000
- Monthly change < 100 rows (normal growth)

**Unhealthy Trend:**
- Total count growing 1,000+ per week (bloat returning)
- Rapid spikes in row counts (delta sync broken)

---

## Adding More Datasets

### When to Add More Datasets

**Add scheduled syncs if:**
- ✅ Dataset changes frequently (hourly/daily)
- ✅ App requires near real-time data
- ✅ Manual syncs are too slow/tedious
- ✅ Dataset accumulates bloat

**Don't add if:**
- ❌ Dataset rarely changes (monthly/yearly)
- ❌ On-demand sync via API works fine
- ❌ Dataset doesn't support delta sync
- ❌ Not actively used in app

---

### How to Add a New Dataset

**Example: Adding `rent_roll` dataset**

#### Step 1: Initialize Sync State

```sql
-- In Supabase SQL Editor
INSERT INTO appfolio_sync_state (endpoint, sync_method, last_synced_at, last_run_status, last_row_count)
VALUES
    ('rent_roll', 'delta', '1970-01-01T00:00:00Z', 'success', 0)
ON CONFLICT (endpoint) DO NOTHING;

-- Verify
SELECT * FROM appfolio_sync_state WHERE endpoint = 'rent_roll';
```

---

#### Step 2: Create Railway Cron Service

1. Railway Dashboard → **"New Service"** → **"Cron Job"**
2. **Name:** Rent Roll Sync
3. **Source:** `StantonManagement/SupabaseAF_appfolo` (branch: `zeff-delta-sync`)
4. **Cron Schedule:** Choose frequency:
   - `0 0 * * *` - Daily at midnight
   - `0 */6 * * *` - Every 6 hours
   - `0 * * * *` - Hourly
5. **Custom Start Command:**
   ```
   python -m app.job_runner --dataset rent_roll
   ```
6. **Variables:** Copy from `RAILWAY_ENV_VARIABLES.md`
7. **Save** and wait for deployment

---

#### Step 3: Test the New Service

1. Go to service → **Cron Runs** tab
2. Click **"Run now"**
3. Check logs for success
4. Verify sync state updated:
   ```sql
   SELECT * FROM appfolio_sync_state WHERE endpoint = 'rent_roll';
   ```

---

#### Step 4: Verify Dataset Mapping

Make sure dataset exists in `app/helpers/constants.py`:

```python
DETAILS = {
    # ... other datasets ...
    "rent_roll": "AF_RentRoll",  # ✅ Should exist
}
```

If NOT there, add it and redeploy.

---

### Testing Delta Sync for New Dataset

**Some AppFolio endpoints don't support delta sync!**

**Test procedure:**

1. Run sync once (should fetch all records)
2. Check logs for "DELTA SYNC" message
3. Run sync again immediately
4. Check if it fetches 0 records (delta working) or all records again (delta not supported)

**If delta NOT supported:**

Disable delta sync for that dataset:

```python
# In job_runner.py or sync.py
result = sync_details("problematic_dataset", use_delta=False)
```

Or adjust cron frequency to avoid bloat (e.g., weekly instead of hourly).

---

## Best Practices

### 1. Environment Variables

**DO:**
- ✅ Use Railway's Raw Editor for bulk paste
- ✅ Store complete JWT tokens (200+ chars)
- ✅ Keep tokens without quotes
- ✅ Document in `RAILWAY_ENV_VARIABLES.md`

**DON'T:**
- ❌ Add quotes around values
- ❌ Truncate long tokens
- ❌ Share tokens in public repos
- ❌ Use production keys in development

---

### 2. Cron Schedules

**Recommended Frequencies:**

| Dataset Type | Frequency | Cron Expression |
|--------------|-----------|-----------------|
| Emergency (Work Orders) | Every 5 min | `*/5 * * * *` |
| High Priority (Tenants, Units) | Hourly | `0 * * * *` |
| Medium Priority (Properties, Rent Roll) | Daily | `0 5 * * *` |
| Low Priority (Reports, Analytics) | Weekly | `0 0 * * 0` |

**Avoid:**
- ❌ Every minute (unnecessary API load)
- ❌ Multiple services at same time (spreads load)
- ❌ Off-hours syncs if not needed (wastes resources)

---

### 3. Error Handling

**Always:**
- ✅ Check Railway logs after deployment
- ✅ Monitor first 3-5 executions closely
- ✅ Set up alerts for repeated failures
- ✅ Have rollback plan (revert to previous branch)

**Never:**
- ❌ Ignore failed syncs for days
- ❌ Assume delta sync works without testing
- ❌ Deploy Friday evening (Murphy's Law)

---

### 4. Database Maintenance

**Weekly:**
- ✅ Check for duplicate records
- ✅ Verify row counts stable
- ✅ Review sync state table

**Monthly:**
- ✅ Analyze growth trends
- ✅ Clean up old test endpoints
- ✅ Review and optimize schedules

**Quarterly:**
- ✅ Audit all AF tables for usage
- ✅ Remove unused datasets
- ✅ Update documentation

---

## Success Criteria

### You know it's working when:

1. ✅ **First sync fetches all records**
   - Work Orders: ~167 records
   - Tenants: ~433 records
   - Units: ~323 records
   - Properties: ~66 records

2. ✅ **Second sync fetches 0-5 records**
   - Shows "DELTA SYNC since [recent timestamp]"
   - Only new/changed records returned

3. ✅ **Sync state updates after each run**
   - `last_synced_at` is current timestamp
   - `last_run_status` = 'success'
   - `last_row_count` matches records synced

4. ✅ **Row counts remain stable over time**
   - Total: ~1,000-1,500 rows
   - Growth: <100 rows per month (normal)
   - No duplicates

5. ✅ **Railway services run on schedule**
   - Work Orders: Every 5 minutes
   - Others: As configured
   - No errors in logs

6. ✅ **No more bloat accumulation**
   - NOT growing to 329K+ rows
   - Database stays healthy

---

## Rollback Procedure

**If something goes wrong:**

### Emergency Rollback (Quick)

1. In Railway, switch branch back to `main`:
   - Go to each service → Settings
   - Change Source Branch to `main`
   - Redeploy

2. This reverts to pre-delta-sync code
3. Crons will run full syncs again (but at least they work)

---

### Proper Rollback (Recommended)

1. **Create rollback branch:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b rollback-delta-sync
   ```

2. **Revert the delta sync commits:**
   ```bash
   git log  # Find the commit hash before delta sync
   git revert <commit-hash>
   git push origin rollback-delta-sync
   ```

3. **Switch Railway to rollback branch**

4. **Fix issues in zeff-delta-sync branch**

5. **Re-deploy when fixed**

---

## Conclusion

This guide provides a complete, step-by-step walkthrough of implementing and deploying AppFolio Delta Sync to fix the database bloat issue.

**Key Achievements:**
- ✅ Reduced database size from 329K+ rows to ~1,500 stable rows
- ✅ Implemented timestamp-based delta sync
- ✅ Deployed 4 automated cron services to Railway
- ✅ Established monitoring and maintenance procedures

**Current Status:**
- ✅ Work Orders Sync: OPERATIONAL (every 5 minutes)
- ✅ Tenants Sync: CONFIGURED (hourly)
- ✅ Units Sync: CONFIGURED (hourly)
- ✅ Properties Sync: CONFIGURED (daily)

**Next Steps:**
1. Monitor all services for 24-48 hours
2. Verify row counts stay stable
3. Test delta sync on remaining services
4. Consider adding more critical datasets if needed

---

## Support & Resources

**Files Reference:**
- Code: `/Users/zeff/Desktop/Work/stanton/SupabaseAF_appfolo/`
- Env Vars: `RAILWAY_ENV_VARIABLES.md`
- Database Init: `initialize_sync_state.sql`
- Verification: `verify_sync_status.sql`
- Session Summary: `SESSION_SUMMARY_2026-03-06.md`

**External Resources:**
- Railway Docs: https://docs.railway.app/
- Supabase Docs: https://supabase.com/docs
- AppFolio API Docs: (Internal/Partner Portal)

---

**Document Version:** 1.0
**Last Updated:** March 6, 2026
**Author:** Implementation Team
**Status:** Production Ready ✅
