# AppFolio API Project Knowledge

## Authentication & Base URLs

### Stack API (REST)
- **Auth Method**: HTTP Basic Auth (Client ID:Client Secret)
- **Base URL**: `https://{database}.appfolio.com/api/v1/`
- **Content-Type**: `application/json`

### Reports API
- **Auth Method**: HTTP Basic Auth (Client ID:Client Secret)  
- **Base URL**: `https://{ClientID}:{ClientSecret}@{database}.appfolio.com/api/v2/reports/`
- **Content-Type**: `application/json`

### Getting Credentials
1. AppFolio Property Manager → Account dropdown → General Settings
2. Manage API Settings → Stack API Credentials (or Reports API Credentials)
3. Generate New Credentials if needed

## Rate Limits

### Stack API
- Standard endpoints: Check documentation
- No rate limits on pagination URLs

### Reports API
- **Limit**: 7 requests per 15 seconds
- **Exception**: `next_page_url` has no rate limits
- **Best Practice**: Stagger requests to avoid 429 errors

## Key Stack API Endpoints

### Properties
- `GET /properties` - List all properties
- Filters: `LastUpdatedAtFrom`, `IncludeHidden`, `PropertyIds`

### Tenants
- `GET /tenants` - List all tenants
- Key fields: `OccupancyId`, `UnitId`, `PropertyId`, `Status`, `MoveInOn`, `MoveOutOn`

### Units
- `GET /units` - List units
- `PUT /units/{id}` - Update unit (e.g., set `RentReady`)
- Filters: `PropertyIds`, `UnitGroupIds`, `LeasingType`, `LastUpdatedAtFrom`

### Charges
- `GET /charges` - Get open charges for occupants
- `POST /charges` - Create single charge
- `POST /charges/bulk` - Bulk create charges

### Bills
- `GET /bills/{id}` - Get specific bill
- `POST /bills` - Create bill
- `POST /bills/bulk` - Bulk create bills
- `PUT /bills/{id}` - Update bill

### Work Orders
- `GET /work_orders` - List work orders
- `POST /work_orders` - Create work order
- `PUT /work_orders/{id}` - Update work order
- Filters: `PropertyId`, `UnitId`, `Statuses`, `LastUpdatedAtFrom`

### Ledgers
- `GET /tenant_ledgers` - Get tenant ledger (charges, payments, credits)
- `GET /community_association_homeowner_ledgers` - Get CA homeowner ledger

### Owners
- `GET /owners` - List owners
- `POST /owners` - Create owner
- `PUT /owners/{id}` - Update owner

### Vendors
- `GET /vendors` - List vendors
- `POST /vendors` - Create vendor
- `PUT /vendors/{id}` - Update vendor

## Key Reports API Endpoints

### Financial Reports
- `/account_totals.json` - Account totals by date range
- `/aged_receivables_detail.json` - Detailed AR aging
- `/aged_payables_summary.json` - AP aging summary
- `/annual_budget_comparative.json` - Budget vs actual
- `/check_register_detail.json` - **Requires** `from_date`
- `/deposit_register.json` - **Requires** `from_date` and `to_date`

### Property Reports
- `/amenities_by_property.json` - Property amenities
- `/balance_sheet.json` - **Requires** `properties` filter

### Tenant Reports
- `/payment_plans.json` - **Requires** `from_date`
- `/receivables_activity.json` - **Requires** `from_date`
- `/rental_applications.json` - **Requires** `from_date`

### Affordable Housing Reports
- `/affordable_housing_hud_waitlist.json`
- `/affordable_housing_program_status.json`
- `/affordable_housing_tenant_demographic.json`
- `/affordable_housing_unit_directory.json`

## Common Filters & Parameters

### Property Filters (used in many endpoints)
```json
{
  "properties": {
    "properties_ids": [],
    "property_groups_ids": [],
    "portfolios_ids": [],
    "owners_ids": []
  }
}
```

### Property Visibility
- `"active"` - Active properties only (default)
- `"hidden"` - Hidden properties only
- `"all"` - All properties

### Accounting Basis
- `"Cash"` (default)
- `"Accrual"`

### Date Filters (common patterns)
- `from_date` / `to_date` - Date range
- `posted_on_from` / `posted_on_to` - Posting date range
- `occurred_on_to` - As of date
- `LastUpdatedAtFrom` - Records updated since date

### Pagination
```json
{
  "paginate_results": true  // Default, max 5000 rows
}
```
- Response includes `next_page_url` for next batch
- POST to `next_page_url` for subsequent pages
- Results valid for 30 minutes
- Set `paginate_results: false` to get all results (slower, use with date filters)

## Data Types

| Type | Format | Example |
|------|--------|---------|
| Amount | String with 2 decimals | `"100.00"` |
| Date | YYYY-MM-DD | `"2023-06-30"` |
| DateTime | ISO 8601 UTC | `"2023-06-30T14:30:00Z"` |
| Number | Integer | `12345` |
| String | UTF-8 | `"Property Name"` |

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 400 | Bad Request | Check request syntax and parameters |
| 401 | Unauthorized | Verify credentials |
| 404 | Not Found | Check endpoint URL |
| 406 | Not Acceptable | Verify Content-Type header |
| 429 | Too Many Requests | Slow down request rate |
| 500 | Server Error | Retry after delay |

## Best Practices

1. **Rate Limiting**: Stagger requests, use `next_page_url` for pagination
2. **Date Filters**: Always include date ranges for large datasets
3. **Required Filters**: Check endpoint documentation for required filters
4. **Pagination**: Use `next_page_url` instead of re-running reports for large datasets
5. **Credentials**: Store securely, never commit to source control
6. **Error Handling**: Implement retry logic for 429 and 500 errors
7. **Testing**: Test with small date ranges first

## Common Request Examples

### Stack API - Get Properties
```bash
curl -X GET \
  'https://{database}.appfolio.com/api/v1/properties' \
  -H 'Authorization: Basic {base64(ClientID:ClientSecret)}' \
  -H 'Content-Type: application/json'
```

### Reports API - Account Totals
```bash
curl -X POST \
  'https://{ClientID}:{ClientSecret}@{database}.appfolio.com/api/v2/reports/account_totals.json' \
  -H 'Content-Type: application/json' \
  -d '{
    "gl_account_ids": "1",
    "posted_on_from": "2023-06-01",
    "posted_on_to": "2023-06-30"
  }'
```

### Stack API - Create Charge
```bash
curl -X POST \
  'https://{database}.appfolio.com/api/v1/charges' \
  -H 'Authorization: Basic {base64(ClientID:ClientSecret)}' \
  -H 'Content-Type: application/json' \
  -d '{
    "occupancy_id": "12345",
    "amount": "100.00",
    "description": "Late Fee",
    "gl_account_id": "67890"
  }'
```

## Useful Queries

### Find all vacant units
Filter units where `CurrentOccupancyId` is null

### Get delinquent tenants
Use `/aged_receivables_detail.json` with `balance_operator` > 0

### Create recurring charges
Use `/recurring_charges` endpoint with `Frequency`, `StartDate`, `EndDate`

### Attach files
Use `/attachments` with corresponding ID (BillId, ChargeId, WorkOrderId, etc.)

## Notes

- **Database URL**: Your specific subdomain (e.g., `stantonmgmt.appfolio.com`)
- **UTC Timezone**: All timestamps are in UTC
- **Next Page URL**: Doesn't accept filter changes - generates new report if filters needed
- **Column Selection**: Use `columns` parameter to limit returned fields for better performance