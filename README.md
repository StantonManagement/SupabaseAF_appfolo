# AppFolio Migration

FastAPI service and support scripts for mirroring AppFolio report data into Supabase tables used by Stanton Management. The project provides a thin REST layer for triggering dataset syncs, shared utilities for normalizing payloads, and sandbox tooling for validating AppFolio and Supabase connectivity.

## Architecture
- `app/main.py` exposes a FastAPI application with `GET /` for health checking and `POST /sync_details` to trigger dataset migrations.
- `app/services/appfolio.py` selects the proper AppFolio Reports (v2) or Stack (v1) endpoint, handling Basic Auth and request dispatch.
- `app/services/supabase_client.py` authenticates with Supabase using the service role key and upserts records into the mapped tables defined in `app/helpers/constants.py`.
- `app/helpers/utils.py` offers `clean_record` to convert numeric strings into typed values before persistence.
- `docs/` captures API research, schema definitions, and sample payloads; `sandbox/` hosts executable diagnostics for API and database access.

## Prerequisites
- Python 3.11 or newer.
- AppFolio Reports API and Stack API credentials.
- Supabase project with matching tables (see `docs/TABLES.md`).
- Optional: `postgresql` client tools for direct Supabase queries.

## Local Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Create a `.env` file at the project root with:
```
APPFOLIO_CLIENT_ID=...
APPFOLIO_CLIENT_SECRET=...
V1_BASE_URL=https://<tenant>.appfolio.com/api/v1
V2_BASE_URL=https://<tenant>.appfolio.com/api/v2/reports
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_ANON_KEY=...        # optional, used by sandbox scripts
DATABASE_URL=postgresql://postgres:<password>@db.<project>.supabase.co:5432/postgres
```

## Running the API
```bash
uvicorn app.main:app --reload
```

## API Reference
- `GET /` → simple health payload `{"Hello": "World"}`.
- `POST /sync_details` accepts `{"dataset": <DETAILS key>}` and returns `{"success": int, "failed": int, "total": int}`, providing counts of successful and failed record upserts.

Sample request:
```bash
curl -X POST http://127.0.0.1:8000/sync_details \
  -H 'Content-Type: application/json' \
  -d '{"dataset": "guest_card_inquiries"}'
```

Sample response:
```json
{
    "success": 150,
    "failed": 2,
    "total": 152
}
```

The service fetches the specified dataset, cleans each record, and upserts it into the Supabase table referenced in `DETAILS`. For v1-only resources (`aged_payables_summary`, `bill_detail`), the client automatically switches to the Stack API.

## Supported Dataset Keys
`DETAILS` currently covers:
`aged_payables_summary`, `bill_detail`, `delinquency`, `gross_potential_rent_enhanced`, `guest_card_inquiries`, `guest_cards`, `inactive_guest_cards`, `lease_expiration_detail`, `lease_expiration_summary`, `lease_history`, `leasing_agent_performance`, `leasing_funnel_performance`, `leasing_summary`, `owner_leasing`, `property_group_directory`, `purchase_order`, `rent_roll`, `rent_roll_commercial`, `rent_roll_itemized`, `rental_applications`, `tenant_debt_collections_status`, `tenant_directory`, `tenant_tickler`, `tenant_vehicle_info`, `unit_turn_detail`, `unit_vacancy`, `work_order`, `work_order_labor_summary`.

## Verification & Troubleshooting
- `sandbox/appfolio_test.py` exercises a wide set of Reports API endpoints with credential validation and rate-limit protection.
- `sandbox/simple_supabase_test.py` and `sandbox/final_supabase_test.py` confirm Supabase REST and Postgres connectivity; the latter prints a corrected `.env` template if connection strings are malformed.
- `sandbox/postgres_test.py` demonstrates direct Postgres access; run only with trusted networks.
- Comprehensive logging is available throughout the sync process:
  - API requests and responses are logged with success/failure details
  - AppFolio API calls show records fetched and any connection issues
  - Supabase operations log each record upsert with individual error tracking
  - Final sync statistics show success, failed, and total counts
  - Job runner emits structured JSON logs for monitoring systems

## Development Guidelines
- Follow standard Python style (PEP 8) with 4-space indents and grouped imports; use snake_case for functions and UpperCamelCase for classes.
- Add new dataset mappings to `app/helpers/constants.py` and ensure Supabase schema updates are mirrored in `docs/TABLES.md`.
- Commit using Conventional Commit prefixes (`feat:`, `fix:`, `chore:`) and document validation steps in pull requests.
- For significant API changes, capture sample payloads in `docs/RESULTS.md` to maintain data lineage.

## Additional Resources
- `docs/appfolio-api-knowledge.md` – canonical guide for authentication nuances, rate limits, and endpoint filters.
- `docs/developer-advice-doc.md` – practical playbook for choosing between Stack and Reports endpoints with code snippets.
- `docs/TABLES.md` – Supabase SQL definitions for provisioned tables.

## Deploy to Railway
Use one public API service and one worker service per dataset (separate schedules and logs).

1) Create Environment Group
- Add `APPFOLIO_CLIENT_ID`, `APPFOLIO_CLIENT_SECRET`, `V1_BASE_URL`, `V2_BASE_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` (optional: `SUPABASE_ANON_KEY`, `DATABASE_URL`). Attach to all services.

2) API Service (single endpoint)
- New Service → GitHub Repository (this repo). Build uses Python Nixpacks.
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port ${PORT}`.
- Verify `GET /` and `POST /sync_details` at the service URL.

3) Worker Services (per dataset)
- Create a new service from the same repo (no port needed).
- Add a Cron for each dataset with the command:
  - `python -m app.job_runner --dataset unit_vacancy`
  - `python -m app.job_runner --dataset rental_applications`
- Example schedules: `*/30 * * * *` (every 30 min), `0 * * * *` (hourly). Stagger to respect AppFolio limits.

4) Logs, Retries, Non-overlap
- Each worker has isolated logs. The runner emits JSON: `{event,dataset,run_id,status,count,duration_ms}`.
- Railway Cron marks failures on non‑zero exit; enable retries/backoff in the Cron settings if available.
- If jobs may run long, keep one dataset per worker; optionally add a lock using a Supabase table.

Manual run examples
- From a worker service “Run command”: `python -m app.job_runner --dataset unit_vacancy`.
- Multiple datasets in one run: `python -m app.job_runner --dataset unit_vacancy,rental_applications`.
