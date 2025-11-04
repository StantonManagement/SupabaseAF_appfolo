===========

-- ProspectSourceTracking
DROP TABLE IF EXISTS "AF_ProspectSourceTracking" CASCADE;

CREATE TABLE "AF_ProspectSourceTracking" (
  "id" SERIAL PRIMARY KEY,

  "source" TEXT,
  "guest_card_inquiries" INTEGER,
  "showings" INTEGER,
  "applications" INTEGER,
  "approved_applications" INTEGER,
  "converted_tenants" INTEGER
);




===========

-- PremiumLeadsBillingDetail
DROP TABLE IF EXISTS "AF_PremiumLeadsBillingDetail" CASCADE;

CREATE TABLE "AF_PremiumLeadsBillingDetail" (
  "id" SERIAL PRIMARY KEY,

  "name" TEXT,
  "charged_date" DATE,
  "refunded_date" DATE,
  "amount" NUMERIC(12, 2),
  "guest_card_id" INTEGER,
  "guest_card_uuid" TEXT,
  "property_id" TEXT,
  "property" TEXT
);

CREATE INDEX "idx_premium_leads_billing_detail_guest_card" ON "AF_PremiumLeadsBillingDetail"("guest_card_id");
CREATE INDEX "idx_premium_leads_billing_detail_property" ON "AF_PremiumLeadsBillingDetail"("property_id");

===========

-- ResidentFinancialActivity
DROP TABLE IF EXISTS "AF_ResidentFinancialActivity" CASCADE;

CREATE TABLE "AF_ResidentFinancialActivity" (
  "id" SERIAL PRIMARY KEY,

  "account" TEXT,
  "account_name" TEXT,
  "account_number" TEXT,
  "unit_address" TEXT,
  "unit_street" TEXT,
  "unit_street2" TEXT,
  "unit_city" TEXT,
  "unit_state" TEXT,
  "unit_zip" TEXT,
  "last_receipt_date" DATE,
  "occupancy_name" TEXT,
  "unit_name" TEXT,
  "property_name" TEXT,
  "payer" TEXT,
  "sum_start_date" NUMERIC(12, 2),
  "sum_charges" NUMERIC(12, 2),
  "sum_payments" NUMERIC(12, 2),
  "sum_end_date" NUMERIC(12, 2)
);

CREATE INDEX "idx_resident_financial_activity_account" ON "AF_ResidentFinancialActivity"("account_number");
CREATE INDEX "idx_resident_financial_activity_unit" ON "AF_ResidentFinancialActivity"("unit_name");
CREATE INDEX "idx_resident_financial_activity_last_receipt" ON "AF_ResidentFinancialActivity"("last_receipt_date");

===========

-- SecurityDepositFundsDetail
DROP TABLE IF EXISTS "AF_SecurityDepositFundsDetail" CASCADE;

CREATE TABLE "AF_SecurityDepositFundsDetail" (
  "id" SERIAL PRIMARY KEY,

  "property" TEXT,
  "property_name" TEXT,
  "property_id" INTEGER,
  "property_address" TEXT,
  "property_street" TEXT,
  "property_street2" TEXT,
  "property_city" TEXT,
  "property_state" TEXT,
  "property_zip" TEXT,
  "unit" TEXT,
  "tenant_name" TEXT,
  "tenant_status" TEXT,
  "move_in" DATE,
  "move_out" DATE,
  "amount" NUMERIC(12, 2),
  "unit_id" INTEGER,
  "occupancy_id" INTEGER,
  "sdr_echeck_eligibility" TEXT
);

CREATE INDEX "idx_security_deposit_funds_property" ON "AF_SecurityDepositFundsDetail"("property_id");
CREATE INDEX "idx_security_deposit_funds_unit" ON "AF_SecurityDepositFundsDetail"("unit_id");
CREATE INDEX "idx_security_deposit_funds_occupancy" ON "AF_SecurityDepositFundsDetail"("occupancy_id");

===========

-- SurveysSummary
DROP TABLE IF EXISTS "AF_SurveysSummary" CASCADE;

CREATE TABLE "AF_SurveysSummary" (
  "id" SERIAL PRIMARY KEY,

  "survey_id" TEXT,
  "survey_type" TEXT,
  "tenant" TEXT,
  "property" TEXT,
  "property_id" TEXT,
  "work_order_number" TEXT,
  "work_order_id" INTEGER,
  "service_request_id" INTEGER,
  "job_description" TEXT,
  "assigned_user" TEXT,
  "vendor_name" TEXT,
  "questions" JSONB,
  "date_sent" DATE,
  "date_received" DATE
);

CREATE INDEX "idx_surveys_summary_survey" ON "AF_SurveysSummary"("survey_id");
CREATE INDEX "idx_surveys_summary_property" ON "AF_SurveysSummary"("property_id");
CREATE INDEX "idx_surveys_summary_work_order" ON "AF_SurveysSummary"("work_order_id");
CREATE INDEX "idx_surveys_summary_service_request" ON "AF_SurveysSummary"("service_request_id");

===========

-- TenantLedger
DROP TABLE IF EXISTS "AF_TenantLedger" CASCADE;

CREATE TABLE "AF_TenantLedger" (
  "id" SERIAL PRIMARY KEY,

  "date" DATE,
  "payer" TEXT,
  "description" TEXT,
  "debit" NUMERIC(12, 2),
  "credit" NUMERIC(12, 2),
  "credit_debit_balance" NUMERIC(12, 2)
);

CREATE INDEX "idx_tenant_ledger_date" ON "AF_TenantLedger"("date");

===========

-- UnitDirectory
DROP TABLE IF EXISTS "AF_UnitDirectory" CASCADE;

CREATE TABLE "AF_UnitDirectory" (
  "id" SERIAL PRIMARY KEY,

  "property" TEXT,
  "property_name" TEXT,
  "property_id" INTEGER,
  "unit_address" TEXT,
  "unit_street" TEXT,
  "unit_street2" TEXT,
  "unit_city" TEXT,
  "unit_state" TEXT,
  "unit_zip" TEXT,
  "unit_name" TEXT,
  "market_rent" NUMERIC(12, 2),
  "marketing_title" TEXT,
  "marketing_description" TEXT,
  "advertised_rent" NUMERIC(12, 2),
  "posted_to_website" TEXT,
  "posted_to_internet" TEXT,
  "you_tube_url" TEXT,
  "default_deposit" NUMERIC(12, 2),
  "sqft" INTEGER,
  "bedrooms" TEXT,
  "bathrooms" TEXT,
  "unit_tags" TEXT,
  "unit_type" TEXT,
  "created_on" DATE,
  "rentable" TEXT,
  "description" TEXT,
  "rent_status" TEXT,
  "legal_rent" NUMERIC(12, 2),
  "application_fee" NUMERIC(12, 2),
  "rent_ready" TEXT,
  "unit_id" INTEGER,
  "computed_market_rent" NUMERIC(12, 2),
  "ready_for_showing_on" DATE,
  "visibility" TEXT,
  "rentable_uid" TEXT,
  "portfolio_id" INTEGER,
  "unit_integration_id" TEXT,
  "unit_amenities" TEXT,
  "unit_appliances" TEXT,
  "unit_utilities" TEXT,
  "billed_as" TEXT
);

CREATE INDEX "idx_unit_directory_property" ON "AF_UnitDirectory"("property_id");
CREATE INDEX "idx_unit_directory_unit" ON "AF_UnitDirectory"("unit_id");
CREATE INDEX "idx_unit_directory_portfolio" ON "AF_UnitDirectory"("portfolio_id");

===========

-- UnitInspection
DROP TABLE IF EXISTS "AF_UnitInspection" CASCADE;

CREATE TABLE "AF_UnitInspection" (
  "id" SERIAL PRIMARY KEY,

  "property" TEXT,
  "property_name" TEXT,
  "property_id" INTEGER,
  "property_address" TEXT,
  "property_street" TEXT,
  "property_street2" TEXT,
  "property_city" TEXT,
  "property_state" TEXT,
  "property_zip" TEXT,
  "unit_name" TEXT,
  "last_inspection_date" DATE,
  "tenant_name" TEXT,
  "tenant_primary_phone_number" TEXT,
  "move_in_date" DATE,
  "move_out_date" DATE,
  "unit_id" INTEGER,
  "occupancy_id" INTEGER,
  "rentable" TEXT,
  "unit_tags" TEXT
);

CREATE INDEX "idx_unit_inspection_property" ON "AF_UnitInspection"("property_id");
CREATE INDEX "idx_unit_inspection_unit" ON "AF_UnitInspection"("unit_id");
CREATE INDEX "idx_unit_inspection_occupancy" ON "AF_UnitInspection"("occupancy_id");

===========

-- UnpaidBalancesByMonth
DROP TABLE IF EXISTS "AF_UnpaidBalancesByMonth" CASCADE;

CREATE TABLE "AF_UnpaidBalancesByMonth" (
  "id" SERIAL PRIMARY KEY,

  "property" TEXT,
  "property_id" INTEGER,
  "unit" TEXT,
  "unit_id" INTEGER,
  "tenant" TEXT,
  "tags" TEXT,
  "tenant_id" INTEGER,
  "occupancy_id" INTEGER,
  "total_unpaid_balance" NUMERIC(12, 2),
  "months" JSONB
);

CREATE INDEX "idx_unpaid_balances_property" ON "AF_UnpaidBalancesByMonth"("property_id");
CREATE INDEX "idx_unpaid_balances_unit" ON "AF_UnpaidBalancesByMonth"("unit_id");
CREATE INDEX "idx_unpaid_balances_tenant" ON "AF_UnpaidBalancesByMonth"("tenant_id");
CREATE INDEX "idx_unpaid_balances_occupancy" ON "AF_UnpaidBalancesByMonth"("occupancy_id");

===========

-- TenantTransactionsSummary
DROP TABLE IF EXISTS "AF_TenantTransactionsSummary" CASCADE;

CREATE TABLE "AF_TenantTransactionsSummary" (
  "id" SERIAL PRIMARY KEY,

  "unit_name" TEXT,
  "occupancy_name" TEXT,
  "occupancy_status" TEXT,
  "beginning_balance" NUMERIC(12, 2),
  "rent_charges" NUMERIC(12, 2),
  "late_charges" NUMERIC(12, 2),
  "other_charges" NUMERIC(12, 2),
  "cash_payments" NUMERIC(12, 2),
  "ns_fs" NUMERIC(12, 2),
  "concessions" NUMERIC(12, 2),
  "other_credits" NUMERIC(12, 2),
  "ending_balance" NUMERIC(12, 2),
  "property_name_address" TEXT,
  "unit_id" INTEGER,
  "occupancy_id" INTEGER,
  "property_id" INTEGER,
  "portfolio_id" INTEGER
);

CREATE INDEX "idx_tenant_transactions_property" ON "AF_TenantTransactionsSummary"("property_id");
CREATE INDEX "idx_tenant_transactions_unit" ON "AF_TenantTransactionsSummary"("unit_id");
CREATE INDEX "idx_tenant_transactions_occupancy" ON "AF_TenantTransactionsSummary"("occupancy_id");
CREATE INDEX "idx_tenant_transactions_portfolio" ON "AF_TenantTransactionsSummary"("portfolio_id");

===========

-- UnitCustomFields
DROP TABLE IF EXISTS "AF_UnitCustomFields" CASCADE;

CREATE TABLE "AF_UnitCustomFields" (
  "id" SERIAL PRIMARY KEY,

  "unit_name" TEXT,
  "unit_id" INTEGER,
  "property_id" INTEGER
);

CREATE INDEX "idx_unit_custom_fields_unit" ON "AF_UnitCustomFields"("unit_id");
CREATE INDEX "idx_unit_custom_fields_property" ON "AF_UnitCustomFields"("property_id");

===========

-- UpcomingActivities
DROP TABLE IF EXISTS "AF_UpcomingActivities" CASCADE;

CREATE TABLE "AF_UpcomingActivities" (
  "id" SERIAL PRIMARY KEY,

  "activity_date" DATE,
  "activity" TEXT,
  "activity_for" TEXT,
  "label" TEXT,
  "property" TEXT,
  "property_name" TEXT,
  "property_id" INTEGER,
  "property_address" TEXT,
  "property_street" TEXT,
  "property_street2" TEXT,
  "property_city" TEXT,
  "property_state" TEXT,
  "property_zip" TEXT,
  "unit_address" TEXT,
  "unit_street" TEXT,
  "unit_street2" TEXT,
  "unit_city" TEXT,
  "unit_state" TEXT,
  "unit_zip" TEXT,
  "created_by" TEXT,
  "completed_by" TEXT,
  "last_edited_by" TEXT,
  "created_on" DATE,
  "completed_on" DATE,
  "last_edited_on" DATE,
  "status" TEXT,
  "assigned_user" TEXT,
  "unit_id" INTEGER,
  "occupancy_id" INTEGER,
  "owner_id" INTEGER,
  "rental_application_id" INTEGER
);

CREATE INDEX "idx_upcoming_activities_property" ON "AF_UpcomingActivities"("property_id");
CREATE INDEX "idx_upcoming_activities_activity_date" ON "AF_UpcomingActivities"("activity_date");
CREATE INDEX "idx_upcoming_activities_unit" ON "AF_UpcomingActivities"("unit_id");
CREATE INDEX "idx_upcoming_activities_occupancy" ON "AF_UpcomingActivities"("occupancy_id");

===========

-- VendorCustomFields
DROP TABLE IF EXISTS "AF_VendorCustomFields" CASCADE;

CREATE TABLE "AF_VendorCustomFields" (
  "id" SERIAL PRIMARY KEY,

  "vendor_name" TEXT,
  "vendor_id" INTEGER
);

CREATE INDEX "idx_vendor_custom_fields_vendor" ON "AF_VendorCustomFields"("vendor_id");

===========

-- VendorDirectory
DROP TABLE IF EXISTS "AF_VendorDirectory" CASCADE;

CREATE TABLE "AF_VendorDirectory" (
  "id" SERIAL PRIMARY KEY,

  "company_name" TEXT,
  "name" TEXT,
  "address" TEXT,
  "street" TEXT,
  "street2" TEXT,
  "city" TEXT,
  "state" TEXT,
  "zip" TEXT,
  "phone_numbers" TEXT,
  "email" TEXT,
  "default_gl_account" TEXT,
  "payment_type" TEXT,
  "send1099" TEXT,
  "workers_comp_expires" TEXT,
  "liability_ins_expires" TEXT,
  "epa_cert_expires" TEXT,
  "auto_ins_expires" TEXT,
  "state_lic_expires" TEXT,
  "contract_expires" TEXT,
  "tags" TEXT,
  "vendor_id" INTEGER,
  "vendor_trades" TEXT,
  "do_not_use_for_work_order" TEXT,
  "terms" TEXT,
  "first_name" TEXT,
  "last_name" TEXT,
  "vendor_integration_id" TEXT,
  "created_by" TEXT,
  "vendor_type" TEXT,
  "portal_activated" TEXT,
  "discount_adjustment" TEXT,
  "markup_adjustment" TEXT
);

CREATE INDEX "idx_vendor_directory_vendor" ON "AF_VendorDirectory"("vendor_id");
CREATE INDEX "idx_vendor_directory_integration" ON "AF_VendorDirectory"("vendor_integration_id");

===========

-- VendorLedger
DROP TABLE IF EXISTS "AF_VendorLedger" CASCADE;

CREATE TABLE "AF_VendorLedger" (
  "id" SERIAL PRIMARY KEY,

  "reference_number" TEXT,
  "bill_date" DATE,
  "due_date" DATE,
  "posting_date" DATE,
  "account" TEXT,
  "account_name" TEXT,
  "account_number" TEXT,
  "property" TEXT,
  "property_name" TEXT,
  "property_id" INTEGER,
  "property_address" TEXT,
  "property_street" TEXT,
  "property_street2" TEXT,
  "property_city" TEXT,
  "property_state" TEXT,
  "property_zip" TEXT,
  "unit" TEXT,
  "payee_name" TEXT,
  "paid" NUMERIC(12, 2),
  "unpaid" NUMERIC(12, 2),
  "check_number" TEXT,
  "payment_date" DATE,
  "description" TEXT,
  "work_order" TEXT,
  "cash_account" TEXT,
  "txn_id" BIGINT,
  "payable_invoice_detail_id" BIGINT,
  "unit_id" BIGINT,
  "quantity" NUMERIC(12, 2),
  "rate" NUMERIC(12, 2),
  "work_order_assignee" TEXT,
  "approval_status" TEXT,
  "approved_by" TEXT,
  "last_approver" TEXT,
  "next_approvers" TEXT,
  "days_pending_approval" TEXT,
  "board_approval_status" TEXT,
  "txn_created_at" TIMESTAMPTZ,
  "txn_updated_at" TIMESTAMPTZ,
  "created_by" TEXT,
  "bank_account" TEXT,
  "vendor_account_number" TEXT,
  "service_from" DATE,
  "service_to" DATE,
  "other_payment_type" TEXT,
  "purchase_order_number" TEXT,
  "purchase_order_id" TEXT,
  "billed_back" TEXT,
  "project" TEXT,
  "project_id" BIGINT,
  "service_request_id" BIGINT,
  "vendor_id" BIGINT,
  "cost_center_name" TEXT,
  "cost_center_number" TEXT,
  "work_order_issue" TEXT,
  "intercompany_party_name" TEXT,
  "intercompany_party_id" BIGINT,
  "work_order_id" BIGINT,
  "party_id" BIGINT,
  "party_type" TEXT
);

CREATE INDEX "idx_vendor_ledger_vendor" ON "AF_VendorLedger"("vendor_id");
CREATE INDEX "idx_vendor_ledger_property" ON "AF_VendorLedger"("property_id");
CREATE INDEX "idx_vendor_ledger_work_order" ON "AF_VendorLedger"("work_order_id");
CREATE INDEX "idx_vendor_ledger_service_request" ON "AF_VendorLedger"("service_request_id");
CREATE INDEX "idx_vendor_ledger_txn" ON "AF_VendorLedger"("txn_id");

<!-- NEW SCHEMA -->



