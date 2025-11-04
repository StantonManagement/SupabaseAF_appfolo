-- InspectionDetail
DROP TABLE IF EXISTS "AF_InspectionDetail" CASCADE;

CREATE TABLE "AF_InspectionDetail" (
  "id" SERIAL PRIMARY KEY,

  "inspection_name" TEXT,
  "property_name" TEXT,
  "unit" TEXT,
  "resident" TEXT,
  "status" TEXT,
  "inspected_on" DATE,
  "marked_done_on" DATE,
  "marked_done_by" TEXT,
  "created_on" DATE,

  "inspection_id" INTEGER,
  "unit_turn_id" INTEGER,
  "property_id" INTEGER,
  "unit_id" INTEGER,
  "occupancy_id" INTEGER
);

CREATE INDEX "idx_inspection_detail_property" ON "AF_InspectionDetail"("property_id");
CREATE INDEX "idx_inspection_detail_unit" ON "AF_InspectionDetail"("unit_id");
CREATE INDEX "idx_inspection_detail_inspection" ON "AF_InspectionDetail"("inspection_id");
CREATE INDEX "idx_inspection_detail_occupancy" ON "AF_InspectionDetail"("occupancy_id");

===========

-- LateFeePolicyComparison
DROP TABLE IF EXISTS "AF_LateFeePolicyComparison" CASCADE;

CREATE TABLE "AF_LateFeePolicyComparison" (
  "id" SERIAL PRIMARY KEY,

  "property_name" TEXT,
  "resident" TEXT,
  "effective_date" DATE,
  "late_fee_type" TEXT,
  "late_fee_base_amount" NUMERIC(12, 2),
  "eligible_charge_type" TEXT,
  "rent_grace_days" INTEGER,
  "rent_grace_day_fixed_day" INTEGER,
  "late_fee_daily_amount" NUMERIC(12, 2),
  "late_fee_grace_balance" NUMERIC(12, 2),
  "max_daily_late_fees_amount" NUMERIC(12, 2),
  "ignore_partial_payments" BOOLEAN,
  "end_date" DATE,
  "property_id" INTEGER,
  "tenant_id" INTEGER,
  "calculate_fee_from" TEXT,
  "custom_policy" TEXT,
  "occupancy_id" INTEGER
);

CREATE INDEX "idx_late_fee_property" ON "AF_LateFeePolicyComparison"("property_id");
CREATE INDEX "idx_late_fee_tenant" ON "AF_LateFeePolicyComparison"("tenant_id");
CREATE INDEX "idx_late_fee_occupancy" ON "AF_LateFeePolicyComparison"("occupancy_id");
CREATE INDEX "idx_late_fee_effective_date" ON "AF_LateFeePolicyComparison"("effective_date");

===========

-- OccupancyCustomFields
DROP TABLE IF EXISTS "AF_OccupancyCustomFields" CASCADE;

CREATE TABLE "AF_OccupancyCustomFields" (
  "id" SERIAL PRIMARY KEY,

  "tenant_name" TEXT,
  "occupancy_id" INTEGER,
  "unit_id" INTEGER,
  "property_id" INTEGER,
  "custom_fields" JSONB
);

CREATE INDEX "idx_occ_custom_fields_occupancy" ON "AF_OccupancyCustomFields"("occupancy_id");
CREATE INDEX "idx_occ_custom_fields_unit" ON "AF_OccupancyCustomFields"("unit_id");
CREATE INDEX "idx_occ_custom_fields_property" ON "AF_OccupancyCustomFields"("property_id");

===========

-- OccupancySummary
DROP TABLE IF EXISTS "AF_OccupancySummary" CASCADE;

CREATE TABLE "AF_OccupancySummary" (
  "id" SERIAL PRIMARY KEY,

  "unit_type" TEXT,
  "number_of_units" INTEGER,
  "occupied" INTEGER,
  "percent_occupied" NUMERIC(5, 2),
  "average_square_feet" NUMERIC(10, 2),
  "average_market_rent" NUMERIC(12, 2),
  "vacant_rented" INTEGER,
  "vacant_unrented" INTEGER,
  "notice_rented" INTEGER,
  "notice_unrented" INTEGER,
  "average_rent" NUMERIC(12, 2),
  "property" TEXT,
  "bedrooms" INTEGER,
  "bathrooms" NUMERIC(4, 2),
  "property_id" INTEGER
);

CREATE INDEX "idx_occupancy_summary_property" ON "AF_OccupancySummary"("property_id");

===========

-- OwnerCustomFields
DROP TABLE IF EXISTS "AF_OwnerCustomFields" CASCADE;

CREATE TABLE "AF_OwnerCustomFields" (
  "id" SERIAL PRIMARY KEY,

  "owner_name" TEXT,
  "owner_id" INTEGER
);

CREATE INDEX "idx_owner_custom_fields_owner" ON "AF_OwnerCustomFields"("owner_id");

===========

-- ProjectDirectory
DROP TABLE IF EXISTS "AF_ProjectDirectory" CASCADE;

CREATE TABLE "AF_ProjectDirectory" (
  "id" SERIAL PRIMARY KEY,

  "name" TEXT,
  "property" TEXT,
  "units" JSONB,
  "start_date" DATE,
  "end_date" DATE,
  "status" TEXT,
  "total_budget" NUMERIC(12, 2),
  "total_paid" NUMERIC(12, 2),
  "total_purchase_order_amount" NUMERIC(12, 2),
  "project_id" INTEGER,
  "property_id" INTEGER,
  "unit_i_ds" TEXT,
  "notes" TEXT
);

CREATE INDEX "idx_project_directory_property" ON "AF_ProjectDirectory"("property_id");
CREATE INDEX "idx_project_directory_project" ON "AF_ProjectDirectory"("project_id");

===========

-- PropertyCustomFields
DROP TABLE IF EXISTS "AF_PropertyCustomFields" CASCADE;

CREATE TABLE "AF_PropertyCustomFields" (
  "id" SERIAL PRIMARY KEY,

  "property" TEXT,
  "property_name" TEXT,
  "property_id" INTEGER
);

CREATE INDEX "idx_property_custom_fields_property" ON "AF_PropertyCustomFields"("property_id");

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
