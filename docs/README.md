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

## Railway Deployment
- In Railway, the FastAPI application appears as the single service card on the left.
- All dataset-specific jobs (e.g., `tenant_directory`, `rent_roll`, `lease_history`) appear as individual service cards on the right. These correspond to the dataset keys supported by this repo and shown below under “Supported Dataset Keys”. Each of these right‑side services runs the job runner described below.

### Production FastAPI Check
- Base URL: `https://supabaseafappfolo-production.up.railway.app`
- Trigger a sync by posting the dataset key to the FastAPI endpoint:

```bash
curl -X POST https://supabaseafappfolo-production.up.railway.app/sync_details \
  -H 'Content-Type: application/json' \
  -d '{"dataset": "tenant_directory"}'
```

Use any dataset listed in this document (for example, `tenant_directory`) as the `dataset` value. The response returns success/failed counts for the run.

### Background Jobs (Right‑Side Services)
- Executor: `app/job_runner.py`
- Railway start command example:

```bash
python -m app.job_runner --dataset bill_detail
```

- You may also run multiple datasets by comma separating:

```bash
python -m app.job_runner --dataset tenant_directory,rent_roll
```

- On success, logs emit a structured JSON line per dataset. A typical success looks like:

```json
{"event":"sync_complete","dataset":"aged_payables_summary","run_id":"68a868ee-deea-43b9-9bde-eb8a25ae615c","status":"success","count":277,"success":277,"failed":0,"duration_ms":16677}
```

- Key fields:
  - `event`: always `sync_complete` per dataset
  - `dataset`: the dataset key processed
  - `run_id`: UUID grouping all datasets in the invocation
  - `status`: `success` or `error`
  - `count`/`success`/`failed`: totals upserted and failed
  - `duration_ms`: end‑to‑end time for that dataset

- On error the line includes `status:"error"` and an `error` message. The process exits non‑zero so Railway can alert/retry.

### Datasets And Source Of Truth
- Implementations in this repo are keyed by the AppFolio report name, referred to as the `dataset` throughout the code and API.
- The complete, authoritative list of AppFolio reports is available in your AppFolio credentials documentation: https://stantonmgmt.appfolio.com/api_credentials/basic_auth_credentials?selected_tab=documentation
- When adding support for a new report, use the exact report name as the dataset key, map it in `app/helpers/constants.py`, and create the corresponding Supabase table before scheduling a job in Railway.

### Wire A New Dataset Service (Railway)
- Pick dataset key
  - Confirm the exact report name from the AppFolio docs above and ensure it appears in `app/helpers/constants.py` with the correct Supabase table.
- Prepare storage
  - Create/verify the Supabase table schema to match expected fields for that report.
- Test locally
  - Run `python -m app.job_runner --dataset <dataset>` and verify the success JSON and inserted rows.
- Create the Railway service card (right side)
  - Start command: `python -m app.job_runner --dataset <dataset>`
  - Copy environment variables from the FastAPI service (left side): `APPFOLIO_*`, `V1_BASE_URL`, `V2_BASE_URL`, `SUPABASE_*`, and any project‑specific variables.
- Deploy and validate
  - Watch logs for `{"event":"sync_complete","status":"success"}` and check Supabase for new/updated rows.
- Optional scheduling
  - Use Railway scheduling to run at desired cadence; one service per dataset keeps runs isolated.

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

## Maintenance
- Health checks
  - FastAPI: `GET /` on the left‑side service should return `{ "Hello": "World" }`.
  - Jobs: filter Railway logs for `event=sync_complete` and `status=error` to spot failures quickly; use `run_id` to correlate a full run.
- Credentials rotation
  - Rotate and update: `APPFOLIO_CLIENT_ID`, `APPFOLIO_CLIENT_SECRET`, `V1_BASE_URL`, `V2_BASE_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` in Railway variables. Avoid logging secrets.
- Dataset changes
  - Add/update mappings in `app/helpers/constants.py`, create/update Supabase tables, and test with `python -m app.job_runner --dataset <name>` before scheduling.
- Dependency updates
  - Modify `requirements.txt` with pinned versions; rebuild Railway. Prefer testing locally in a venv first.
- Operations playbook
  - Re-run a failed dataset by invoking the job runner for that dataset; upserts are idempotent.
  - Scale right‑side services as needed; each service runs exactly `app/job_runner.py` for its dataset.
  - Keep `docs/RESULTS.md` updated with any payload or schema discoveries.

## Development Guidelines
- Follow standard Python style (PEP 8) with 4-space indents and grouped imports; use snake_case for functions and UpperCamelCase for classes.
- Add new dataset mappings to `app/helpers/constants.py` and ensure Supabase schema updates are mirrored in `docs/TABLES.md`.
- Commit using Conventional Commit prefixes (`feat:`, `fix:`, `chore:`) and document validation steps in pull requests.
- For significant API changes, capture sample payloads in `docs/RESULTS.md` to maintain data lineage.

## Additional Resources
- `docs/appfolio-api-knowledge.md` – canonical guide for authentication nuances, rate limits, and endpoint filters.
- `docs/developer-advice-doc.md` – practical playbook for choosing between Stack and Reports endpoints with code snippets.
## Supabase Tables

Here are the AppFolio report tables that are currently being synced to Supabase:

| Report Name | Table Name |
|-------------|------------|
| unit_vacancy | AF_UnitVacancyDetail |
| rental_applications | AF_RentalApplications |
| guest_cards | AF_GuestCards |
| guest_card_inquiries | AF_GuestCardInquiries |
| inactive_guest_cards | AF_InactiveGuestCards |
| owner_leasing | AF_OwnerLeasing |
| lease_history | AF_LeaseHistory |
| leasing_summary | AF_LeasingSummary |
| leasing_agent_performance | AF_LeasingAgentPerformance |
| leasing_funnel_performance | AF_LeasingFunnelPerformance |
| lease_expiration_detail | AF_LeaseExpirationDetail |
| lease_expiration_summary | AF_LeaseExpirationSummary |
| property_group_directory | AF_PropertyGroupDirectory |
| aged_payables_summary | AF_AgedPayablesSummary |
| bill_detail | AF_BillDetail |
| tenant_directory | AF_TenantDirectory |
| tenant_tickler | AF_TenantTickler |
| tenant_vehicle_info | AF_TenantVehicleInfo |
| tenant_debt_collections_status | AF_TenantDebtCollectionsStatus |
| delinquency | AF_Delinquency |
| gross_potential_rent_enhanced | AF_GrossPotentialRentEnhanced |
| purchase_order | AF_PurchaseOrder |
| rent_roll | AF_RentRoll |
| rent_roll_itemized | AF_RentRollItemized |
| rent_roll_commercial | AF_RentRollCommercial |
| unit_turn_detail | AF_UnitTurnDetail |
| work_order | AF_WorkOrder |
| work_order_labor_summary | AF_WorkOrderLaborSummary |
