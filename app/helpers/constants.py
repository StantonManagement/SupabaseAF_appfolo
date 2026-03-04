DETAILS = {
    # ! important
    "unit_vacancy": "AF_UnitVacancyDetail",
    "rental_applications": "AF_RentalApplications",
    "guest_cards": "AF_GuestCards",
    "guest_card_inquiries": "AF_GuestCardInquiries",
    "inactive_guest_cards": "AF_InactiveGuestCards",
    "owner_leasing": "AF_OwnerLeasing",
    "lease_history": "AF_LeaseHistory",
    "leasing_summary": "AF_LeasingSummary",
    "leasing_agent_performance": "AF_LeasingAgentPerformance",
    "leasing_funnel_performance": "AF_LeasingFunnelPerformance",
    "lease_expiration_detail": "AF_LeaseExpirationDetail",
    "lease_expiration_summary": "AF_LeaseExpirationSummary",
    # ! others
    "property_group_directory": "AF_PropertyGroupDirectory",
    "aged_payables_summary": "AF_AgedPayablesSummary",
    "bill_detail": "AF_BillDetail",
    "tenant_directory": "AF_TenantDirectory",
    "tenant_tickler": "AF_TenantTickler",
    "tenant_vehicle_info": "AF_TenantVehicleInfo",
    "tenant_debt_collections_status": "AF_TenantDebtCollectionsStatus",
    "delinquency": "AF_Delinquency",
    "gross_potential_rent_enhanced": "AF_GrossPotentialRentEnhanced",
    "purchase_order": "AF_PurchaseOrder",
    "rent_roll": "AF_RentRoll",
    "rent_roll_itemized": "AF_RentRollItemized",
    "rent_roll_commercial": "AF_RentRollCommercial",
    "unit_turn_detail": "AF_UnitTurnDetail",
    "work_order": "AF_WorkOrder",
    "work_order_labor_summary": "AF_WorkOrderLaborSummary",
    # ! NEW
    "delinquency_as_of": "AF_DelinquencyAsOf",
    "eligible_debt_summary": "AF_EligibleDebtSummary",
    "email_delivery_errors": "AF_EmailDeliveryErrors",
    "fixed_assets": "AF_FixedAssets",
    "inspection_detail": "AF_InspectionDetail",
    "late_fee_policy_comparison": "AF_LateFeePolicyComparison",
    "occupancy_custom_fields": "AF_OccupancyCustomFields",
    "occupancy_summary": "AF_OccupancySummary",
    "owner_custom_fields": "AF_OwnerCustomFields",
    "project_directory": "AF_ProjectDirectory",
    "property_custom_fields": "AF_PropertyCustomFields",
    "prospect_source_tracking": "AF_ProspectSourceTracking",
    "premium_leads_billing_detail": "AF_PremiumLeadsBillingDetail",
    "resident_financial_activity": "AF_ResidentFinancialActivity",
    "security_deposit_funds_detail": "AF_SecurityDepositFundsDetail",
    "surveys_summary": "AF_SurveysSummary",
    "tenant_ledger": "AF_TenantLedger",
    "unit_directory": "AF_UnitDirectory",
    "unit_inspection": "AF_UnitInspection",
    "unpaid_balances_by_month": "AF_UnpaidBalancesByMonth",
    "tenant_transactions_summary": "AF_TenantTransactionsSummary",
    "unit_custom_fields": "AF_UnitCustomFields",
    "upcoming_activities": "AF_UpcomingActivities",
    "vendor_custom_fields": "AF_VendorCustomFields",
    "vendor_directory": "AF_VendorDirectory",
    "vendor_ledger": "AF_VendorLedger",
    "property_directory": "AF_buildings",
    # ! CANNOT GET DATA FROM THE FF:
    # payment_plans
    # premium_listing_billing_detail
    # project_budget_detail
    # property_budget
    # property_staff_assignments
    # amenities_by_property
    # additional_fees
    # annual_budget_comparative
    # annual_budget_forecast
    # balance_sheet
    # budget_comparative
    # budget_property_comparison
    # cancelled_processes
    # cash_flow
    # tenant_unpaid_charges_summary
    # twelve_month_cash_flow
    # completed_workflows
    # historical_advertised_rent
    # in_progress_workflows
    # income_statement_property_comparison
    # income_statement_property_comparison
    # inventory_usage
    # keys_detail
    # income_statement_comparison
    # renewal_summary
    # showings
    # rentable_items
}


v1_dataset = ["aged_payables_summary", "bill_detail"]

# Stack API (v1) endpoints
stack_api_dataset = []

# Datasets with no unique business key — truncate table before each sync
TRUNCATE_BEFORE_SYNC = [
    "upcoming_activities",
    "resident_financial_activity",
    "premium_leads_billing_detail",
    "prospect_source_tracking",
]

# Per-dataset upsert conflict column (defaults to primary key if not set)
ON_CONFLICT = {
    "property_directory":              "id",
    "unit_vacancy":                    "unit_id",
    "unit_turn_detail":                "unit_turn_id",
    "unit_directory":                  "unit_id",
    "unit_inspection":                 "unit_id",
    "unit_custom_fields":              "unit_id",
    # NEW tables
    "surveys_summary":                 "survey_id",
    "vendor_directory":                "vendor_id",
    "vendor_custom_fields":            "vendor_id",
    "security_deposit_funds_detail":   "occupancy_id",
    "unpaid_balances_by_month":        "occupancy_id",
    "tenant_transactions_summary":     "occupancy_id",
    "vendor_ledger":                   "txn_id",
    "tenant_ledger":                   "date,payer,description,debit,credit",
}

# Per-dataset field mapping: API snake_case key → exact table column name.
# Only fields listed here are sent to Supabase; everything else is dropped.
# Use this when a table uses quoted PascalCase column names that don't match the API.
FIELD_MAP = {
    "property_directory": {
        # PascalCase columns (existing table schema)
        "property":               "Property",
        "property_name":          "PropertyName",
        "property_id":            "PropertyId",
        "property_integration_id":"id",
        "property_address":       "PropertyAddress",
        "property_street":        "PropertyStreet1",
        "property_street2":       "PropertyStreet2",
        "property_city":          "PropertyCity",
        "property_state":         "PropertyState",
        "property_zip":           "PropertyZip",
        "property_county":        "PropertyCounty",
        "market_rent":            "MarketRent",
        "units":                  "Units",
        "sqft":                   "SqFt",
        "management_flat_fee":    "ManagementFlatFee",
        "management_fee_percent": "ManagementFeePercent",
        "minimum_fee":            "MinimumFee",
        "maximum_fee":            "MaximumFee",
        "description":            "Description",
        "portfolio_id":           "PortfolioId",
        "property_group_id":      "PropertyGroupId",
        "property_type":          "PropertyType",
        "property_created_on":    "PropertyCreatedOn",
        "property_created_by":    "PropertyCreatedBy",
        "year_built":             "YearBuilt",
        "amenities":              "Amenities",
        # snake_case columns (newly added)
        "waive_fees_when_vacant":                   "waive_fees_when_vacant",
        "reserve":                                  "reserve",
        "home_warranty_expiration":                 "home_warranty_expiration",
        "insurance_expiration":                     "insurance_expiration",
        "tax_year_end":                             "tax_year_end",
        "tax_authority":                            "tax_authority",
        "owners_phone_number":                      "owners_phone_number",
        "payer_name":                               "payer_name",
        "premium_leads_status":                     "premium_leads_status",
        "premium_leads_monthly_cap":                "premium_leads_monthly_cap",
        "premium_leads_activation_date":            "premium_leads_activation_date",
        "owner_i_ds":                               "owner_i_ds",
        "portfolio_uuid":                           "portfolio_uuid",
        "visibility":                               "visibility",
        "maintenance_limit":                        "maintenance_limit",
        "maintenance_notes":                        "maintenance_notes",
        "site_manager_name":                        "site_manager_name",
        "site_manager_phone_number":                "site_manager_phone_number",
        "management_fee_type":                      "management_fee_type",
        "lease_fee_type":                           "lease_fee_type",
        "lease_flat_fee":                           "lease_flat_fee",
        "lease_fee_percent":                        "lease_fee_percent",
        "renewal_fee_type":                         "renewal_fee_type",
        "renewal_flat_fee":                         "renewal_flat_fee",
        "renewal_fee_percent":                      "renewal_fee_percent",
        "future_management_fee_start_date":         "future_management_fee_start_date",
        "future_management_fee_percent":            "future_management_fee_percent",
        "future_management_flat_fee":               "future_management_flat_fee",
        "future_minimum_fee":                       "future_minimum_fee",
        "future_maximum_fee":                       "future_maximum_fee",
        "future_management_fee_type":               "future_management_fee_type",
        "future_waive_fees_when_vacant":            "future_waive_fees_when_vacant",
        "owner_payment_type":                       "owner_payment_type",
        "owners":                                   "owners",
        "accounting_basis":                         "accounting_basis",
        "prepayment_type":                          "prepayment_type",
        "late_fee_type":                            "late_fee_type",
        "late_fee_base_amount":                     "late_fee_base_amount",
        "late_fee_daily_amount":                    "late_fee_daily_amount",
        "late_fee_grace_period":                    "late_fee_grace_period",
        "late_fee_grace_period_fixed_day":          "late_fee_grace_period_fixed_day",
        "late_fee_grace_balance":                   "late_fee_grace_balance",
        "max_daily_late_fees_amount":               "max_daily_late_fees_amount",
        "ignore_partial_payments":                  "ignore_partial_payments",
        "contract_expirations":                     "contract_expirations",
        "management_start_date":                    "management_start_date",
        "management_end_date":                      "management_end_date",
        "management_end_reason":                    "management_end_reason",
        "agent_of_record":                          "agent_of_record",
        "tax_region_code":                          "tax_region_code",
        "property_class":                           "property_class",
        "online_maintenance_request_instructions":  "online_maintenance_request_instructions",
        "listing_type":                             "listing_type",
    },
}
