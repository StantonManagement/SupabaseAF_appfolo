===========
===========
===========

-- Drop existing table if it exists
DROP TABLE IF EXISTS "AF_GuestCardInquiries" CASCADE;

CREATE TABLE "AF_GuestCardInquiries" (
  "id" SERIAL PRIMARY KEY,
  
  -- Inquiry Metadata
  "name" TEXT,
  "email_address" TEXT,
  "phone_number" TEXT,
  "received" TIMESTAMPTZ,
  "last_activity_date" DATE,
  "last_activity_type" TEXT,
  "latest_interest_date" DATE,
  "latest_interest_source" TEXT,
  "status" TEXT,
  "move_in_preference" DATE,
  
  -- Financial Preferences
  "max_rent" NUMERIC(10, 2),
  "bed_bath_preference" TEXT,
  "pet_preference" TEXT,
  "monthly_income" NUMERIC(12, 2),
  "credit_score" INTEGER,
  
  -- Lead & Property Context
  "lead_type" TEXT,
  "source" TEXT,
  "property" TEXT,
  "unit" TEXT,
  "assigned_user" TEXT,
  "assigned_user_id" INTEGER,
  
  -- Identifiers
  "guest_card_id" INTEGER,
  "guest_card_uuid" UUID,
  "inquiry_id" INTEGER,
  "occupancy_id" INTEGER,
  "property_id" INTEGER,
  "unit_id" INTEGER,
  "tenant_id" INTEGER,
  "rental_application_id" INTEGER,
  "rental_application_group_id" INTEGER,
  
  -- Additional Details
  "notes" TEXT,
  "applicants" JSONB,
  "inquiry_type" TEXT,
  "total_interests_received" INTEGER,
  "interests_received_in_range" INTEGER,
  "showings" INTEGER,
  "interest_to_showing_scheduled" NUMERIC(10, 2),
  "showing_to_application_received" NUMERIC(10, 2),
  "application_received_to_decision" NUMERIC(10, 2),
  "application_submission_to_lease_signed" NUMERIC(10, 2),
  "inquiry_to_lease_signed" NUMERIC(10, 2),
  "inactive_reason" TEXT,
  "crm" TEXT
);

CREATE INDEX "idx_guest_card_inquiries_property" ON "AF_GuestCardInquiries"("property_id");
CREATE INDEX "idx_guest_card_inquiries_guest_card" ON "AF_GuestCardInquiries"("guest_card_id");
CREATE INDEX "idx_guest_card_inquiries_inquiry" ON "AF_GuestCardInquiries"("inquiry_id");
CREATE INDEX "idx_guest_card_inquiries_assigned_user" ON "AF_GuestCardInquiries"("assigned_user_id");

===========
===========
===========

-- Drop existing table if it exists
DROP TABLE IF EXISTS "AF_InactiveGuestCards" CASCADE;

CREATE TABLE "AF_InactiveGuestCards" (
  "id" SERIAL PRIMARY KEY,
  
  -- Guest Card Details
  "name" TEXT,
  "email_address" TEXT,
  "phone_number" TEXT,
  "received" TIMESTAMPTZ,
  "property_name" TEXT,
  "property" TEXT,
  "property_id" INTEGER,
  "unit" TEXT,
  "reason" TEXT,
  "comments" TEXT,
  "lead_type" TEXT,
  "source" TEXT,
  
  -- Identifiers
  "guest_card_id" INTEGER,
  "guest_card_uuid" UUID
);

CREATE INDEX "idx_inactive_guest_cards_property" ON "AF_InactiveGuestCards"("property_id");
CREATE INDEX "idx_inactive_guest_cards_guest_card" ON "AF_InactiveGuestCards"("guest_card_id");

===========
===========
===========

-- Drop existing table if it exists
DROP TABLE IF EXISTS "AF_OwnerLeasing" CASCADE;

CREATE TABLE "AF_OwnerLeasing" (
  "id" SERIAL PRIMARY KEY,
  
  -- Property & Unit Context
  "property" TEXT,
  "unit" TEXT,
  "applied_to" TEXT,
  "unit_type" TEXT,
  "property_id" INTEGER,
  "unit_id" INTEGER,
  
  -- Leasing Metrics
  "market_rent" NUMERIC(10, 2),
  "computed_market_rent" NUMERIC(10, 2),
  "inquiries" INTEGER,
  "showings" INTEGER,
  "applications" INTEGER,
  "approved_applications" INTEGER,
  "converted_tenants" INTEGER
);

CREATE INDEX "idx_owner_leasing_property" ON "AF_OwnerLeasing"("property_id");
CREATE INDEX "idx_owner_leasing_unit" ON "AF_OwnerLeasing"("unit_id");

===========
===========
===========

-- Drop existing table if it exists
DROP TABLE IF EXISTS "AF_LeaseHistory" CASCADE;

CREATE TABLE "AF_LeaseHistory" (
  "id" SERIAL PRIMARY KEY,
  
  -- Property & Unit Context
  "unit_name" TEXT,
  "property" TEXT,
  "property_name" TEXT,
  "property_id" INTEGER,
  "property_address" TEXT,
  "property_street" TEXT,
  "property_street2" TEXT,
  "property_city" TEXT,
  "property_state" TEXT,
  "property_zip" TEXT,
  "unit_type" TEXT,
  "unit_id" INTEGER,
  
  -- Tenant & Occupancy
  "tenant_visibility" TEXT,
  "occupancy_name" TEXT,
  "tenant_name" TEXT,
  "occupancy_id" INTEGER,
  "tenant_id" INTEGER,
  
  -- Lease Terms
  "lease_start" DATE,
  "lease_end" DATE,
  "rent" NUMERIC(10, 2),
  "most_recent_rent" NUMERIC(10, 2),
  "market_rent" NUMERIC(10, 2),
  "status" TEXT,
  "sent_date" DATE,
  "signed_on_date" DATE,
  "countersigned_date" DATE,
  "countersigned_by" TEXT,
  "countersigned_by_id" INTEGER,
  "renewal" TEXT,
  "security_deposit" NUMERIC(10, 2),
  "move_in" DATE,
  "move_out" DATE,
  "time_from_sending_to_signing" NUMERIC(10, 2),
  "time_from_sending_to_countersigning" NUMERIC(10, 2),
  
  -- Audit Fields
  "created_at" DATE,
  "updated_at" DATE,
  
  -- Identifiers
  "lease_uuid" UUID,
  "lease_document_uuid" UUID,
  "inquiry_id" INTEGER
);

CREATE INDEX "idx_lease_history_property" ON "AF_LeaseHistory"("property_id");
CREATE INDEX "idx_lease_history_unit" ON "AF_LeaseHistory"("unit_id");
CREATE INDEX "idx_lease_history_occupancy" ON "AF_LeaseHistory"("occupancy_id");
CREATE INDEX "idx_lease_history_tenant" ON "AF_LeaseHistory"("tenant_id");
CREATE INDEX "idx_lease_history_lease_uuid" ON "AF_LeaseHistory"("lease_uuid");

===========
===========
===========

-- Drop existing table if it exists
DROP TABLE IF EXISTS "AF_LeasingSummary" CASCADE;

CREATE TABLE "AF_LeasingSummary" (
  "id" SERIAL PRIMARY KEY,
  
  -- Aggregated Metrics
  "unit_type" TEXT,
  "number_of_units" INTEGER,
  "number_of_model_units" INTEGER,
  "inquiries_received" INTEGER,
  "showings_completed" INTEGER,
  "applications_received" INTEGER,
  "move_ins" INTEGER,
  "move_outs" INTEGER,
  "leased" INTEGER,
  "vacancy_postings" INTEGER,
  "number_of_active_campaigns" INTEGER,
  "number_of_ended_campaigns" INTEGER
);

CREATE INDEX "idx_leasing_summary_unit_type" ON "AF_LeasingSummary"("unit_type");

===========
===========
===========

-- Drop existing table if it exists
DROP TABLE IF EXISTS "AF_LeasingAgentPerformance" CASCADE;

CREATE TABLE "AF_LeasingAgentPerformance" (
  "id" SERIAL PRIMARY KEY,
  
  -- Agent Performance Metrics
  "assigned_user" TEXT,
  "assigned_user_id" INTEGER,
  "guest_cards" INTEGER,
  "showings" INTEGER,
  "applications" INTEGER,
  "leased_units" INTEGER
);

CREATE INDEX "idx_leasing_agent_performance_user" ON "AF_LeasingAgentPerformance"("assigned_user_id");

===========
===========
===========

-- Drop existing table if it exists
DROP TABLE IF EXISTS "AF_LeasingFunnelPerformance" CASCADE;

CREATE TABLE "AF_LeasingFunnelPerformance" (
  "id" SERIAL PRIMARY KEY,
  
  -- Assignment & Property Context
  "assigned_inquiry_owner" TEXT,
  "assigned_inquiry_owner_id" INTEGER,
  "property_name" TEXT,
  "property_id" INTEGER,
  
  -- Funnel Counts
  "inquiries" INTEGER,
  "completed_showings" INTEGER,
  "cancelled_showings" INTEGER,
  "rental_apps" INTEGER,
  "decision_pending" INTEGER,
  "approved" INTEGER,
  "denied" INTEGER,
  "cancelled" INTEGER,
  "signed_leases" INTEGER,
  "move_ins" INTEGER,
  
  -- Conversion Rates
  "inquiries_to_completed_showings" NUMERIC(6, 2),
  "completed_showings_to_apps" NUMERIC(6, 2),
  "approved_app_rate" NUMERIC(6, 2),
  "apps_to_signed_leases" NUMERIC(6, 2),
  "inquiries_to_leases" NUMERIC(6, 2)
);

CREATE INDEX "idx_leasing_funnel_property" ON "AF_LeasingFunnelPerformance"("property_id");
CREATE INDEX "idx_leasing_funnel_owner" ON "AF_LeasingFunnelPerformance"("assigned_inquiry_owner_id");

===========
===========
===========

-- Drop existing table if it exists
DROP TABLE IF EXISTS "AF_LeaseExpirationDetail" CASCADE;

CREATE TABLE "AF_LeaseExpirationDetail" (
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
  
  -- Unit & Tenant Context
  "unit" TEXT,
  "unit_tags" TEXT,
  "unit_type" TEXT,
  "unit_id" INTEGER,
  "tenant_name" TEXT,
  "tenant_id" INTEGER,
  
  -- Lease Timeline
  "move_in" DATE,
  "lease_expires" DATE,
  "lease_expires_month" TEXT,
  "move_out" DATE,
  "last_rent_increase" DATE,
  "next_rent_adjustment" DATE,
  "next_rent_increase" DATE,
  "lease_sign_date" DATE,
  "last_lease_renewal" DATE,
  "renewal_start_date" DATE,
  "notice_given_date" DATE,
  
  -- Financials
  "market_rent" NUMERIC(10, 2),
  "computed_market_rent" NUMERIC(10, 2),
  "sqft" INTEGER,
  "deposit" NUMERIC(10, 2),
  "rent" NUMERIC(10, 2),
  "legal_rent" NUMERIC(10, 2),
  
  -- Contact & Ownership
  "phone_numbers" TEXT,
  "owners_phone_number" TEXT,
  "owners" TEXT,
  "owner_agent" TEXT,
  "tenant_agent" TEXT,
  
  -- Status & Tags
  "status" TEXT,
  "rent_status" TEXT,
  "tenant_tags" TEXT,
  "affordable_program" TEXT,
  "occupancy_id" INTEGER
);

CREATE INDEX "idx_lease_expiration_detail_property" ON "AF_LeaseExpirationDetail"("property_id");
CREATE INDEX "idx_lease_expiration_detail_unit" ON "AF_LeaseExpirationDetail"("unit_id");
CREATE INDEX "idx_lease_expiration_detail_tenant" ON "AF_LeaseExpirationDetail"("tenant_id");
CREATE INDEX "idx_lease_expiration_detail_occupancy" ON "AF_LeaseExpirationDetail"("occupancy_id");

===========
===========
===========

-- Drop existing table if it exists
DROP TABLE IF EXISTS "AF_LeaseExpirationSummary" CASCADE;

CREATE TABLE "AF_LeaseExpirationSummary" (
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
  
  -- Aggregated Metrics
  "units" INTEGER,
  "months" JSONB,
  "total" INTEGER
);

CREATE INDEX "idx_lease_expiration_summary_property" ON "AF_LeaseExpirationSummary"("property_id");

===========
===========
===========

===========
===========
===========

-- Drop existing table if it exists
DROP TABLE IF EXISTS "AF_PurchaseOrder" CASCADE;

CREATE TABLE "AF_PurchaseOrder" (
  "id" SERIAL PRIMARY KEY,
  
  -- Financial Totals
  "item_subtotal" NUMERIC(12, 2),
  "tax_estimate" NUMERIC(12, 2),
  "shipping_estimate" NUMERIC(12, 2),
  "amount" NUMERIC(12, 2),
  "sum_of_bills" NUMERIC(12, 2),
  "billed_amount" NUMERIC(12, 2),
  
  -- Purchase Order Identification
  "purchase_order_number" TEXT,
  "purchase_order_id" INTEGER,
  "work_orders" TEXT,
  "party_type" TEXT,
  
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
  
  -- Account & Project Links
  "account" TEXT,
  "account_name" TEXT,
  "account_number" TEXT,
  "account_id" INTEGER,
  "project" TEXT,
  "project_id" INTEGER,
  
  -- Unit & Vendor Details
  "unit_name" TEXT,
  "unit_id" INTEGER,
  "vendor_name" TEXT,
  "vendor_id" INTEGER,
  "shipped_to" TEXT,
  
  -- Status & Approvals
  "approval_status" TEXT,
  "last_approver" TEXT,
  "last_approved_on" TIMESTAMPTZ,
  "received" TEXT,
  "completed" TEXT,
  "canceled" TEXT,
  
  -- Dates & Ownership
  "created_at" DATE,
  "created_by" TEXT,
  "updated_at" DATE,
  "required_by" DATE,
  "order_submitted_date" DATE,
  
  -- Additional Details
  "description" TEXT,
  "instructions" TEXT,
  "all_bills" JSONB,
  "revision_instructions" TEXT,
  "revision_assignee" TEXT,
  "revision_requester" TEXT,
  "revision_requested_date" TIMESTAMPTZ,
  "revision_completed_date" TIMESTAMPTZ
);

CREATE INDEX "idx_purchase_order_property" ON "AF_PurchaseOrder"("property_id");
CREATE INDEX "idx_purchase_order_unit" ON "AF_PurchaseOrder"("unit_id");
CREATE INDEX "idx_purchase_order_vendor" ON "AF_PurchaseOrder"("vendor_id");
CREATE INDEX "idx_purchase_order_po" ON "AF_PurchaseOrder"("purchase_order_id");

===========
===========
===========

-- Drop existing table if it exists
DROP TABLE IF EXISTS "AF_RentRoll" CASCADE;

CREATE TABLE "AF_RentRoll" (
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
  "property_type" TEXT,
  "property_group_id" TEXT,
  "portfolio_id" TEXT,
  
  -- Unit & Occupancy
  "occupancy_id" INTEGER,
  "unit_id" INTEGER,
  "unit" TEXT,
  "unit_tags" TEXT,
  "unit_type" TEXT,
  "bd_ba" TEXT,
  "sqft" INTEGER,
  "building_id" INTEGER,
  
  -- Tenant Information
  "tenant" TEXT,
  "tenant_id" INTEGER,
  "additional_tenants" TEXT,
  "additional_tenant_ids" TEXT,
  "tenant_tags" TEXT,
  "tenant_agent" TEXT,
  "occupancy_import_uid" TEXT,
  "affordable_program" TEXT,
  
  -- Financial Metrics
  "market_rent" NUMERIC(12, 2),
  "advertised_rent" NUMERIC(12, 2),
  "computed_market_rent" NUMERIC(12, 2),
  "rent" NUMERIC(12, 2),
  "deposit" NUMERIC(12, 2),
  "monthly_market_rent_square_ft" NUMERIC(12, 2),
  "annual_market_rent_square_ft" NUMERIC(12, 2),
  "monthly_rent_square_ft" NUMERIC(12, 2),
  "annual_rent_square_ft" NUMERIC(12, 2),
  "past_due" NUMERIC(12, 2),
  "application_fee" NUMERIC(12, 2),
  "amenities_price" NUMERIC(12, 2),
  "legal_rent" NUMERIC(12, 2),
  "preferential_rent" NUMERIC(12, 2),
  "next_rent_increase_amount" NUMERIC(12, 2),
  "previous_occupancy_rent" NUMERIC(12, 2),
  "previous_rent" NUMERIC(12, 2),
  
  -- Timeline
  "lease_from" DATE,
  "lease_to" DATE,
  "move_in" DATE,
  "move_out" DATE,
  "last_move_out" DATE,
  "last_rent_increase" DATE,
  "next_rent_adjustment" DATE,
  "next_rent_increase" DATE,
  "lease_expires_month" TEXT,
  
  -- Operational Status
  "status" TEXT,
  "status_by_square_feet" TEXT,
  "rent_ready" TEXT,
  "rent_status" TEXT,
  "amenities" TEXT,
  "monthly_charges" JSONB,
  "nsf" INTEGER,
  "late" INTEGER
);

CREATE INDEX "idx_rent_roll_property" ON "AF_RentRoll"("property_id");
CREATE INDEX "idx_rent_roll_unit" ON "AF_RentRoll"("unit_id");
CREATE INDEX "idx_rent_roll_occupancy" ON "AF_RentRoll"("occupancy_id");
CREATE INDEX "idx_rent_roll_tenant" ON "AF_RentRoll"("tenant_id");

===========
===========
===========

-- Drop existing table if it exists
DROP TABLE IF EXISTS "AF_RentRollItemized" CASCADE;

CREATE TABLE "AF_RentRollItemized" (
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
  "property_type" TEXT,
  "property_group_id" TEXT,
  "portfolio_id" TEXT,
  
  -- Unit & Tenant
  "occupancy_id" INTEGER,
  "unit_id" INTEGER,
  "unit" TEXT,
  "unit_tags" TEXT,
  "unit_type" TEXT,
  "bd_ba" TEXT,
  "tenant" TEXT,
  "tenant_tags" TEXT,
  "tenant_agent" TEXT,
  "sqft" INTEGER,
  
  -- Financial Breakdown
  "market_rent" NUMERIC(12, 2),
  "computed_market_rent" NUMERIC(12, 2),
  "advertised_rent" NUMERIC(12, 2),
  "total" NUMERIC(12, 2),
  "other_charges" NUMERIC(12, 2),
  "monthly_rent_square_ft" NUMERIC(12, 2),
  "annual_rent_square_ft" NUMERIC(12, 2),
  "deposit" NUMERIC(12, 2),
  
  -- Lease Timeline
  "lease_from" DATE,
  "lease_to" DATE,
  "last_rent_increase" DATE,
  "next_rent_adjustment" DATE,
  "next_rent_increase_amount" NUMERIC(12, 2),
  "next_rent_increase" DATE,
  "move_in" DATE,
  "move_out" DATE,
  
  -- Operational Status
  "status" TEXT,
  "past_due" NUMERIC(12, 2),
  "nsf" INTEGER,
  "late" INTEGER,
  "amenities" TEXT,
  "additional_tenants" TEXT,
  "monthly_charges" JSONB,
  "rent_ready" TEXT,
  "rent_status" TEXT,
  "legal_rent" NUMERIC(12, 2),
  "preferential_rent" NUMERIC(12, 2)
);

CREATE INDEX "idx_rent_roll_itemized_property" ON "AF_RentRollItemized"("property_id");
CREATE INDEX "idx_rent_roll_itemized_unit" ON "AF_RentRollItemized"("unit_id");
CREATE INDEX "idx_rent_roll_itemized_occupancy" ON "AF_RentRollItemized"("occupancy_id");

===========
===========
===========

-- Drop existing table if it exists
DROP TABLE IF EXISTS "AF_RentRollCommercial" CASCADE;

CREATE TABLE "AF_RentRollCommercial" (
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
  "property_group_id" TEXT,
  "portfolio_id" TEXT,
  
  -- Unit & Lease Grouping
  "unit_name" TEXT,
  "unit_id" INTEGER,
  "occupant_name" TEXT,
  "occupancy_id" INTEGER,
  "group_name" TEXT,
  "gl_account" TEXT,
  "sqft" INTEGER,
  
  -- Financial Metrics
  "charge_amount" NUMERIC(12, 2),
  "amount_as_monthly" NUMERIC(12, 2),
  "monthly_amount_per_sq_ft" NUMERIC(12, 2),
  "12_month_amount" NUMERIC(12, 2),
  "12_month_amount_per_sq_ft" NUMERIC(12, 2),
  
  -- Lease Options
  "start_date" DATE,
  "end_date" DATE,
  "lease_option_dates" TEXT,
  "lease_option_terms" TEXT,
  "lease_option_descriptions" TEXT,
  "tenant_tags" TEXT
);

CREATE INDEX "idx_rent_roll_commercial_property" ON "AF_RentRollCommercial"("property_id");
CREATE INDEX "idx_rent_roll_commercial_unit" ON "AF_RentRollCommercial"("unit_id");

===========
===========
===========

-- Drop existing table if it exists
DROP TABLE IF EXISTS "AF_UnitTurnDetail" CASCADE;

CREATE TABLE "AF_UnitTurnDetail" (
  "id" SERIAL PRIMARY KEY,
  
  -- Property Context
  "property" TEXT,
  "property_id" INTEGER,
  
  -- Unit Context
  "unit" TEXT,
  "unit_id" INTEGER,
  "unit_turn_id" INTEGER,
  
  -- Scheduling
  "move_out_date" DATE,
  "turn_end_date" DATE,
  "expected_move_in_date" DATE,
  "target_days_to_complete" INTEGER,
  "total_days_to_complete" INTEGER,
  
  -- Costs & Labor
  "labor_from_work_orders" NUMERIC(12, 2),
  "purchase_orders_from_work_orders" NUMERIC(12, 2),
  "billables_from_work_orders" NUMERIC(12, 2),
  "inventory_from_work_orders" NUMERIC(12, 2),
  "total_billed" NUMERIC(12, 2),
  
  -- Notes
  "notes" TEXT,
  "reference_user" TEXT
);

CREATE INDEX "idx_unit_turn_detail_property" ON "AF_UnitTurnDetail"("property_id");
CREATE INDEX "idx_unit_turn_detail_unit" ON "AF_UnitTurnDetail"("unit_id");
CREATE INDEX "idx_unit_turn_detail_turn" ON "AF_UnitTurnDetail"("unit_turn_id");

===========
===========
===========

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

-- Drop existing table if it exists
DROP TABLE IF EXISTS "AF_WorkOrderLaborSummary" CASCADE;

CREATE TABLE "AF_WorkOrderLaborSummary" (
  "id" SERIAL PRIMARY KEY,
  
  -- Raw payload storage (structure not returned in sample)
  "raw_record" JSONB
);

-- No indexes created due to absent schema details
