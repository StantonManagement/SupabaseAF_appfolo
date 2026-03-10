# Available AppFolio Tables

## Currently Scheduled (4 tables)
✅ **Active with Delta Sync**

1. `work_order` → AF_WorkOrder (every 5 min)
2. `tenant_directory` → AF_TenantDirectory (hourly)
3. `unit_directory` → AF_UnitDirectory (hourly)
4. `property_group_directory` → AF_PropertyGroupDirectory (daily)

---

## Available for On-Demand Sync (54 tables)

### Leasing & Occupancy (11 tables)
- `unit_vacancy` → AF_UnitVacancyDetail
- `rental_applications` → AF_RentalApplications
- `guest_cards` → AF_GuestCards
- `guest_card_inquiries` → AF_GuestCardInquiries
- `inactive_guest_cards` → AF_InactiveGuestCards
- `owner_leasing` → AF_OwnerLeasing
- `lease_history` → AF_LeaseHistory
- `leasing_summary` → AF_LeasingSummary
- `leasing_agent_performance` → AF_LeasingAgentPerformance
- `leasing_funnel_performance` → AF_LeasingFunnelPerformance
- `occupancy_summary` → AF_OccupancySummary

### Lease Management (3 tables)
- `lease_expiration_detail` → AF_LeaseExpirationDetail
- `lease_expiration_summary` → AF_LeaseExpirationSummary
- `occupancy_custom_fields` → AF_OccupancyCustomFields

### Financial & Billing (8 tables)
- `aged_payables_summary` → AF_AgedPayablesSummary
- `bill_detail` → AF_BillDetail
- `delinquency` → AF_Delinquency
- `delinquency_as_of` → AF_DelinquencyAsOf
- `eligible_debt_summary` → AF_EligibleDebtSummary
- `gross_potential_rent_enhanced` → AF_GrossPotentialRentEnhanced
- `purchase_order` → AF_PurchaseOrder
- `tenant_debt_collections_status` → AF_TenantDebtCollectionsStatus

### Rent & Revenue (3 tables)
- `rent_roll` → AF_RentRoll
- `rent_roll_itemized` → AF_RentRollItemized
- `rent_roll_commercial` → AF_RentRollCommercial

### Tenant Management (6 tables)
- `tenant_tickler` → AF_TenantTickler
- `tenant_vehicle_info` → AF_TenantVehicleInfo
- `tenant_ledger` → AF_TenantLedger
- `tenant_transactions_summary` → AF_TenantTransactionsSummary
- `resident_financial_activity` → AF_ResidentFinancialActivity
- `unpaid_balances_by_month` → AF_UnpaidBalancesByMonth

### Work Orders & Maintenance (2 tables)
- `work_order_labor_summary` → AF_WorkOrderLaborSummary
- `unit_turn_detail` → AF_UnitTurnDetail

### Properties & Buildings (2 tables)
- `buildings` → AF_Buildings (uses property_group_directory data)
- `property_custom_fields` → AF_PropertyCustomFields

### Units (2 tables)
- `unit_inspection` → AF_UnitInspection
- `unit_custom_fields` → AF_UnitCustomFields

### Vendors (3 tables)
- `vendor_directory` → AF_VendorDirectory
- `vendor_ledger` → AF_VendorLedger
- `vendor_custom_fields` → AF_VendorCustomFields

### Projects & Assets (3 tables)
- `project_directory` → AF_ProjectDirectory
- `fixed_assets` → AF_FixedAssets
- `security_deposit_funds_detail` → AF_SecurityDepositFundsDetail

### Communications & Other (9 tables)
- `email_delivery_errors` → AF_EmailDeliveryErrors
- `inspection_detail` → AF_InspectionDetail
- `late_fee_policy_comparison` → AF_LateFeePolicyComparison
- `owner_custom_fields` → AF_OwnerCustomFields
- `prospect_source_tracking` → AF_ProspectSourceTracking
- `premium_leads_billing_detail` → AF_PremiumLeadsBillingDetail
- `surveys_summary` → AF_SurveysSummary
- `upcoming_activities` → AF_UpcomingActivities

---

## Tables That CANNOT Be Synced

These AppFolio endpoints don't work or aren't available:

- payment_plans
- premium_listing_billing_detail
- project_budget_detail
- property_budget
- property_staff_assignments
- amenities_by_property
- additional_fees
- annual_budget_comparative
- annual_budget_forecast
- balance_sheet
- budget_comparative
- budget_property_comparison
- cancelled_processes
- cash_flow
- tenant_unpaid_charges_summary
- twelve_month_cash_flow
- completed_workflows
- historical_advertised_rent
- in_progress_workflows
- income_statement_property_comparison
- inventory_usage
- keys_detail
- income_statement_comparison
- renewal_summary
- showings
- rentable_items

---

## Recommendation: Which to Add Next?

### High Value Tables (Consider adding):

**Financial Data (Daily sync):**
- `rent_roll` - Current tenant rent
- `delinquency` - Late payments
- `tenant_ledger` - Transaction history

**Operations (Daily/Weekly sync):**
- `vendor_directory` - Vendors
- `unit_vacancy` - Available units
- `lease_expiration_detail` - Upcoming renewals

**Analytics (Weekly sync):**
- `occupancy_summary` - Property metrics
- `work_order_labor_summary` - Maintenance costs

### Low Priority (Keep on-demand):
- All custom_fields tables
- Historical/archived data tables
- Rarely changing reference data

---

## How to Add a New Table

### Step 1: Check Unique Constraint

Run in Supabase:
```sql
SELECT
    conname as constraint_name,
    a.attname as column_name
FROM pg_constraint c
JOIN pg_class t ON c.conrelid = t.oid
JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(c.conkey)
WHERE t.relname = 'AF_RentRoll'  -- Change table name
    AND c.contype = 'u';
```

### Step 2: Add to Code

In `app/helpers/constants.py`:
```python
UPSERT_CONFLICT_FIELDS = {
    # ... existing ...
    "rent_roll": "occupancy_id",  # Use the unique field from Step 1
}
```

### Step 3: Create Railway Service

- Name: Rent Roll Sync
- Command: `python -m app.job_runner --dataset rent_roll`
- Schedule: `0 0 * * *` (daily at midnight)
- Environment Variables: Copy from existing services

### Step 4: Initialize Sync State

In Supabase SQL Editor:
```sql
INSERT INTO appfolio_sync_state (endpoint, sync_method, last_synced_at, last_run_status, last_row_count)
VALUES ('rent_roll', 'delta', '1970-01-01T00:00:00Z', 'success', 0)
ON CONFLICT (endpoint) DO NOTHING;
```

### Step 5: Test

1. Manually trigger sync
2. Check logs for success
3. Verify database updated

---

**Created:** March 9, 2026
**Status:** Reference document for future expansion
