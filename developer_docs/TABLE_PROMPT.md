Based on this json data:

FOR DATASET:  inspection_detail
{
  "inspection_name": "Inspection_110 Martin Street Unit 7",
  "property_name": "S0011 - 110 Martin",
  "unit": "7",
  "resident": null,
  "status": "NEW",
  "inspected_on": "2025-01-20",
  "marked_done_on": null,
  "marked_done_by": null,
  "created_on": "2025-01-20",
  "inspection_id": 39,
  "unit_turn_id": null,
  "property_id": 44,
  "unit_id": 309,
  "occupancy_id": null
}
--------------------

FOR DATASET:  late_fee_policy_comparison
{
  "property_name": "Northend Portfolio (For Loan Booking Only)",
  "resident": null,
  "effective_date": "2025-06-01",
  "late_fee_type": "Flat",
  "late_fee_base_amount": "5.00",
  "eligible_charge_type": "Recurring Only",
  "rent_grace_days": 10,
  "rent_grace_day_fixed_day": null,
  "late_fee_daily_amount": "5.00",
  "late_fee_grace_balance": "0.00",
  "max_daily_late_fees_amount": "45.00",
  "ignore_partial_payments": null,
  "end_date": null,
  "property_id": 85,
  "tenant_id": null,
  "calculate_fee_from": null,
  "custom_policy": null,
  "occupancy_id": null
}
--------------------

FOR DATASET:  occupancy_custom_fields
{
  "tenant_name": "Bueno Grocery LLC",
  "occupancy_id": 137,
  "unit_id": 157,
  "property_id": 17,
  "custom_fields": [
    {
      "name": "On Payment Plan",
      "value": "No"
    }
  ]
}

--------------------

FOR DATASET:  occupancy_summary
{
  "unit_type": "2 bedroom Apt.",
  "number_of_units": 0,
  "occupied": 0,
  "percent_occupied": null,
  "average_square_feet": null,
  "average_market_rent": null,
  "vacant_rented": 0,
  "vacant_unrented": 0,
  "notice_rented": 0,
  "notice_unrented": 0,
  "average_rent": null,
  "property": "S0020 - 31 Park - 31-33 Park St Hartford, CT 06106",
  "bedrooms": 2,
  "bathrooms": "1.00",
  "property_id": 142
}
--------------------


FOR DATASET:  owner_custom_fields
{
  "owner_name": "Stanton REP 90 Park Street Hartford LLC",
  "owner_id": 5
}
--------------------




FOR DATASET:  project_directory
{
  "name": "110 martin Roof Replacement",
  "property": "S0011 - 110 Martin - 110 Martin St Hartford, CT 06120",
  "units": null,
  "start_date": null,
  "end_date": null,
  "status": null,
  "total_budget": 0,
  "total_paid": 0,
  "total_purchase_order_amount": 0,
  "project_id": 4,
  "property_id": 44,
  "unit_i_ds": null,
  "notes": "07/28/2023, Awaiting CHFA approval"
}
--------------------



FOR DATASET:  property_custom_fields
{
  "property": "S0001 - 90 Park St - 90-100 Park Street Hartford, CT 06106",
  "property_name": "S0001 - 90 Park St",
  "property_id": 17
}
--------------------

FOR DATASET:  prospect_source_tracking
{
  "source": "Apartment List",
  "guest_card_inquiries": 53,
  "showings": 0,
  "applications": 1,
  "approved_applications": 0,
  "converted_tenants": 0
}
--------------------








I want you to put the create a table schema for our supabase and put it in TABLES.md like so:

if work_order is the report name (dataset), the table name should be WorkOrder (in PascalCase)

-- Drop existing table if it exists
DROP TABLE IF EXISTS "AF_WorkOrder" CASCADE;

CREATE TABLE "AF_WorkOrder" (
  "id" SERIAL PRIMARY KEY,
  
  -- Property Context
  "property" TEXT,
  "property_name" TEXT,
  "property_id" INTEGER,
  "property_address" TEXT,
  "property_street" TEXT,
  "property_street2" TEXT,
  "property_city" TEXT,
  "property_state" TEXT,
  "property_zip" TEXT,
  
  -- Unit Context
  "unit_address" TEXT,
  "unit_street" TEXT,
  "unit_street2" TEXT,
  "unit_city" TEXT,
  "unit_state" TEXT,
  "unit_zip" TEXT,
  "unit_name" TEXT,
  "unit_id" INTEGER,
  
  -- Request & Work Order IDs
  "work_order_id" INTEGER,
  "work_order_number" TEXT,
  "service_request_id" INTEGER,
  "service_request_number" TEXT,
  "unit_turn_id" INTEGER,
  
  -- Priority & Type
  "priority" TEXT,
  "work_order_type" TEXT,
  "work_order_issue" TEXT,
  "unit_turn_category" TEXT,
  
  -- Status Tracking
  "status" TEXT,
  "status_notes" TEXT,
  "recurring" TEXT,
  "submitted_by_tenant" TEXT,
  "follow_up_on" TIMESTAMPTZ,
  
  -- Vendor & Assignment
  "vendor" TEXT,
  "vendor_id" INTEGER,
  "vendor_trade" TEXT,
  "vendor_portal_invoices" INTEGER,
  "assigned_user" TEXT,
  
  -- Tenant Context
  "occupancy_id" INTEGER,
  "primary_tenant" TEXT,
  "primary_tenant_email" TEXT,
  "primary_tenant_phone_number" TEXT,
  "requesting_tenant" TEXT,
  
  -- Description & Instructions
  "service_request_description" TEXT,
  "job_description" TEXT,
  "instructions" TEXT,
  
  -- Dates
  "created_at" DATE,
  "created_by" TEXT,
  "home_warranty_expiration" DATE,
  "estimate_req_on" TIMESTAMPTZ,
  "estimated_on" TIMESTAMPTZ,
  "estimate_approved_on" TIMESTAMPTZ,
  "estimate_approval_last_requested_on" TIMESTAMPTZ,
  "scheduled_start" TIMESTAMPTZ,
  "scheduled_end" TIMESTAMPTZ,
  "work_completed_on" TIMESTAMPTZ,
  "completed_on" TIMESTAMPTZ,
  "last_billed_on" TIMESTAMPTZ,
  "canceled_on" TIMESTAMPTZ,
  "inspection_date" TIMESTAMPTZ,
  
  -- Financial Metrics
  "amount" NUMERIC(12, 2),
  "invoice" TEXT,
  "estimate_amount" NUMERIC(12, 2),
  "corporate_charge_amount" NUMERIC(12, 2),
  "corporate_charge_id" INTEGER,
  "discount_amount" NUMERIC(12, 2),
  "discount_bill_id" INTEGER,
  "markup_amount" NUMERIC(12, 2),
  "markup_bill_id" INTEGER,
  "tenant_total_charge_amount" NUMERIC(12, 2),
  "tenant_charge_ids" TEXT,
  "vendor_bill_amount" NUMERIC(12, 2),
  "vendor_bill_id" INTEGER,
  "vendor_charge_amount" NUMERIC(12, 2),
  "vendor_charge_id" INTEGER,
  "maintenance_limit" NUMERIC(12, 2),
  
  -- Approvals & Surveys
  "estimate_approval_status" TEXT,
  "survey_id" INTEGER,
  
  -- Additional Context
  "inspection_id" INTEGER
);

CREATE INDEX "idx_work_order_property" ON "AF_WorkOrder"("property_id");
CREATE INDEX "idx_work_order_unit" ON "AF_WorkOrder"("unit_id");
CREATE INDEX "idx_work_order_service_request" ON "AF_WorkOrder"("service_request_id");
CREATE INDEX "idx_work_order_work_order" ON "AF_WorkOrder"("work_order_id");
CREATE INDEX "idx_work_order_occupancy" ON "AF_WorkOrder"("occupancy_id");

===========
===========
===========


Do that for all the endpoints that are put before. 