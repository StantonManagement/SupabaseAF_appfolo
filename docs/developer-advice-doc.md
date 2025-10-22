# Developer Instructions: AppFolio-Supabase Sync Setup

## Step-by-Step Implementation Guide

### Step 1: Understand the Two APIs

AppFolio has **two different APIs** with different endpoints:

#### Reports API (v2)
- **Base URL**: `https://stantonmgmt.appfolio.com/api/v2/reports/`
- **Endpoint Pattern**: `{report_name}.json`
- **Method**: POST
- **Auth**: Basic Auth with Reports API credentials

**Working Reports API Endpoints:**
```
✅ bill_detail.json
✅ aged_receivables_detail.json
✅ rent_roll.json
✅ work_order.json
✅ chart_of_accounts.json
✅ general_ledger.json
✅ aged_payables_summary.json
✅ deposit_register.json
✅ receivables_activity.json
✅ rental_applications.json
```

#### Stack API (v1)
- **Base URL**: `https://stantonmgmt.appfolio.com/api/v1/`
- **Endpoint Pattern**: `{resource}` (no .json)
- **Method**: GET or POST
- **Auth**: Basic Auth with Stack API credentials

**Stack API Endpoints (for buildings, portfolios, etc.):**
```
✅ properties          (not "buildings")
✅ property_groups     (includes portfolios)
✅ units
✅ tenants
✅ owners
✅ vendors
✅ work_orders
```

### Step 2: Find the Correct Endpoint Names

**For buildings/properties:**
```bash
# WRONG - This doesn't exist
https://stantonmgmt.appfolio.com/api/v2/reports/buildings.json ❌

# CORRECT - Use Stack API
https://stantonmgmt.appfolio.com/api/v1/properties ✅
```

**For portfolios:**
```bash
# WRONG - This doesn't exist
https://stantonmgmt.appfolio.com/api/v2/reports/portfolios.json ❌

# CORRECT - Use Stack API property_groups
https://stantonmgmt.appfolio.com/api/v1/property_groups ✅
```

### Step 3: Test Endpoints Before Building Tables

Create a test script to verify endpoints work:

```typescript
// test-endpoints.ts
const STACK_BASE = 'https://stantonmgmt.appfolio.com/api/v1'
const REPORTS_BASE = 'https://stantonmgmt.appfolio.com/api/v2/reports'

const stackAuth = btoa(`${STACK_CLIENT_ID}:${STACK_CLIENT_SECRET}`)
const reportsAuth = btoa(`${REPORTS_CLIENT_ID}:${REPORTS_CLIENT_SECRET}`)

// Test Stack API endpoint
async function testStackAPI(endpoint: string) {
  const url = `${STACK_BASE}/${endpoint}`
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Authorization': `Basic ${stackAuth}`,
      'Content-Type': 'application/json'
    }
  })
  
  if (response.ok) {
    const data = await response.json()
    console.log(`✅ ${endpoint} works!`)
    console.log('Sample data:', JSON.stringify(data[0], null, 2))
    return data
  } else {
    console.error(`❌ ${endpoint} failed: ${response.status}`)
    console.error(await response.text())
  }
}

// Test Reports API endpoint
async function testReportsAPI(endpoint: string) {
  const url = `${REPORTS_BASE}/${endpoint}.json`
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Basic ${reportsAuth}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ property_visibility: 'active' })
  })
  
  if (response.ok) {
    const data = await response.json()
    console.log(`✅ ${endpoint} works!`)
    console.log('Sample data:', JSON.stringify(data.results?.[0] || data[0], null, 2))
    return data
  } else {
    console.error(`❌ ${endpoint} failed: ${response.status}`)
    console.error(await response.text())
  }
}

// Run tests
console.log('Testing Stack API...')
await testStackAPI('properties')
await testStackAPI('property_groups')
await testStackAPI('units')
await testStackAPI('tenants')

console.log('\nTesting Reports API...')
await testReportsAPI('bill_detail')
await testReportsAPI('aged_receivables_detail')
await testReportsAPI('rent_roll')
```

**Run it:**
```bash
deno run --allow-net test-endpoints.ts
```

### Step 4: Create Tables with Correct Schema

**CRITICAL: Always quote table and column names to preserve case!**

#### Example: Properties (from Stack API)

```sql
-- Drop existing table if it exists
DROP TABLE IF EXISTS "AF_Properties" CASCADE;

-- Create table with proper data types and case-sensitive column names
CREATE TABLE "AF_Properties" (
  -- Primary Key (UUID)
  "id" UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  
  -- AppFolio ID (this is their unique identifier)
  "PropertyId" TEXT UNIQUE NOT NULL,
  
  -- Basic Information
  "Name" TEXT,
  "PropertyType" TEXT,
  
  -- Address
  "Address1" TEXT,
  "Address2" TEXT,
  "City" TEXT,
  "State" TEXT,
  "Zip" TEXT,
  
  -- Additional Fields
  "MaintenanceNotes" TEXT,
  "TenantPortalLink" TEXT,
  "PropertyGroupIds" TEXT[], -- Array of group IDs
  
  -- Metadata
  "HiddenAt" TIMESTAMPTZ,
  "LastUpdatedAt" TIMESTAMPTZ,
  
  -- Sync Metadata
  "synced_at" TIMESTAMPTZ DEFAULT NOW(),
  "sync_status" TEXT DEFAULT 'success'
);

-- Create indexes for frequently queried columns
CREATE INDEX "idx_properties_propertyid" ON "AF_Properties"("PropertyId");
CREATE INDEX "idx_properties_city" ON "AF_Properties"("City");
CREATE INDEX "idx_properties_type" ON "AF_Properties"("PropertyType");
CREATE INDEX "idx_properties_synced" ON "AF_Properties"("synced_at");
```

#### Example: Property Groups/Portfolios (from Stack API)

```sql
-- Drop existing table if it exists
DROP TABLE IF EXISTS "AF_PropertyGroups" CASCADE;

-- Create table
CREATE TABLE "AF_PropertyGroups" (
  -- Primary Key (UUID)
  "id" UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  
  -- AppFolio ID
  "PropertyGroupId" TEXT UNIQUE NOT NULL,
  
  -- Group Information
  "Name" TEXT,
  "Type" TEXT, -- "Portfolio", "Group", etc.
  
  -- Metadata
  "LastUpdatedAt" TIMESTAMPTZ,
  
  -- Sync Metadata
  "synced_at" TIMESTAMPTZ DEFAULT NOW(),
  "sync_status" TEXT DEFAULT 'success'
);

-- Create indexes
CREATE INDEX "idx_propertygroups_id" ON "AF_PropertyGroups"("PropertyGroupId");
CREATE INDEX "idx_propertygroups_type" ON "AF_PropertyGroups"("Type");
```

#### Example: Units (from Stack API)

```sql
-- Drop existing table if it exists
DROP TABLE IF EXISTS "AF_Units" CASCADE;

-- Create table
CREATE TABLE "AF_Units" (
  -- Primary Key (UUID)
  "id" UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  
  -- AppFolio ID
  "UnitId" TEXT UNIQUE NOT NULL,
  
  -- Relationships
  "PropertyId" TEXT,
  
  -- Unit Information
  "Name" TEXT,
  "UnitType" TEXT,
  "Bedrooms" INTEGER,
  "Bathrooms" NUMERIC(3, 1),
  "SquareFeet" INTEGER,
  "MarketRent" NUMERIC(12, 2),
  
  -- Occupancy
  "CurrentOccupancyId" TEXT,
  "RentReady" BOOLEAN,
  
  -- Metadata
  "HiddenAt" TIMESTAMPTZ,
  "LastUpdatedAt" TIMESTAMPTZ,
  
  -- Sync Metadata
  "synced_at" TIMESTAMPTZ DEFAULT NOW(),
  "sync_status" TEXT DEFAULT 'success'
);

-- Create indexes
CREATE INDEX "idx_units_unitid" ON "AF_Units"("UnitId");
CREATE INDEX "idx_units_propertyid" ON "AF_Units"("PropertyId");
CREATE INDEX "idx_units_occupancy" ON "AF_Units"("CurrentOccupancyId");
CREATE INDEX "idx_units_rentready" ON "AF_Units"("RentReady");
```

### Step 5: Map API Response to Table Columns

When syncing, you need to map AppFolio field names to your table columns:

```typescript
// For Stack API - Properties
async function syncProperties(appfolio, supabase) {
  console.log('Syncing AF_Properties...')
  
  // Get data from Stack API
  const data = await appfolio.stackRequest('properties')
  
  // Clear existing data
  await supabase.from('AF_Properties').delete().neq('id', 0)
  
  // Map AppFolio fields to Supabase columns
  const mapped = data.map((p: any) => ({
    PropertyId: p.Id,                    // AppFolio uses "Id"
    Name: p.Name,
    PropertyType: p.PropertyType,
    Address1: p.Address1,
    Address2: p.Address2,
    City: p.City,
    State: p.State,
    Zip: p.Zip,
    MaintenanceNotes: p.MaintenanceNotes,
    TenantPortalLink: p.TenantPortalLink,
    PropertyGroupIds: p.PropertyGroupIds,
    HiddenAt: p.HiddenAt,
    LastUpdatedAt: p.LastUpdatedAt,
    synced_at: new Date().toISOString(),
    sync_status: 'success'
  }))
  
  // Insert in batches
  const BATCH_SIZE = 1000
  for (let i = 0; i < mapped.length; i += BATCH_SIZE) {
    const batch = mapped.slice(i, i + BATCH_SIZE)
    const { error } = await supabase.from('AF_Properties').insert(batch)
    if (error) throw error
  }
  
  console.log(`✓ Synced ${mapped.length} properties`)
}

// For Stack API - Property Groups
async function syncPropertyGroups(appfolio, supabase) {
  console.log('Syncing AF_PropertyGroups...')
  
  const data = await appfolio.stackRequest('property_groups')
  
  await supabase.from('AF_PropertyGroups').delete().neq('id', 0)
  
  const mapped = data.map((pg: any) => ({
    PropertyGroupId: pg.Id,
    Name: pg.Name,
    Type: pg.Type,
    LastUpdatedAt: pg.LastUpdatedAt,
    synced_at: new Date().toISOString(),
    sync_status: 'success'
  }))
  
  const { error } = await supabase.from('AF_PropertyGroups').insert(mapped)
  if (error) throw error
  
  console.log(`✓ Synced ${mapped.length} property groups`)
}

// For Reports API - Bill Detail (already working)
async function syncBillDetail(appfolio, supabase) {
  console.log('Syncing AF_BillDetail...')
  
  const { results } = await appfolio.getAllReportData('bill_detail', {
    property_visibility: 'active'
  })
  
  await supabase.from('AF_BillDetail').delete().neq('id', 0)
  
  const mapped = results.map((b: any) => ({
    // Map every field from API response to your table columns
    PayableInvoiceDetailID: b.payable_invoice_detail_id,
    TxnId: b.txn_id,
    ReferenceNumber: b.reference_number,
    BillDate: b.bill_date,
    DueDate: b.due_date,
    // ... map all other fields
    synced_at: new Date().toISOString(),
    sync_status: 'success'
  }))
  
  const BATCH_SIZE = 1000
  for (let i = 0; i < mapped.length; i += BATCH_SIZE) {
    const batch = mapped.slice(i, i + BATCH_SIZE)
    const { error } = await supabase.from('AF_BillDetail').insert(batch)
    if (error) throw error
  }
  
  console.log(`✓ Synced ${mapped.length} bill detail records`)
}
```

### Step 6: Handle Field Name Differences

AppFolio's API returns fields in different formats:

**Stack API** (properties, units, etc.):
- Uses PascalCase: `PropertyId`, `FirstName`, `LastName`

**Reports API** (bill_detail, aged_receivables, etc.):
- Uses snake_case: `property_id`, `first_name`, `last_name`

**Solution:** Always check the actual API response first!

```typescript
// Add debug logging to see actual field names
async function debugAPIResponse(endpoint: string, isReports = false) {
  const data = isReports 
    ? await appfolio.reportsRequest(endpoint, {})
    : await appfolio.stackRequest(endpoint)
  
  const sample = isReports ? (data.results?.[0] || data[0]) : data[0]
  
  console.log(`\n=== ${endpoint} Field Names ===`)
  console.log(Object.keys(sample))
  console.log('\nSample Record:')
  console.log(JSON.stringify(sample, null, 2))
}

// Run this before creating tables
await debugAPIResponse('properties', false)        // Stack API
await debugAPIResponse('property_groups', false)   // Stack API
await debugAPIResponse('bill_detail', true)        // Reports API
```

### Step 7: Complete Working Example

Here's a complete sync function that works for both APIs:

```typescript
// supabase/functions/sync-appfolio/index.ts

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

class AppFolioClient {
  private database: string
  private stackAuth: string
  private reportsAuth: string

  constructor(database: string, stackId: string, stackSecret: string, 
              reportsId: string, reportsSecret: string) {
    this.database = database
    this.stackAuth = btoa(`${stackId}:${stackSecret}`)
    this.reportsAuth = btoa(`${reportsId}:${reportsSecret}`)
  }

  // Stack API request (GET)
  async stackRequest(endpoint: string) {
    const url = `https://${this.database}.appfolio.com/api/v1/${endpoint}`
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Authorization': `Basic ${this.stackAuth}`,
        'Content-Type': 'application/json',
      }
    })

    if (!response.ok) {
      throw new Error(`Stack API ${response.status}: ${await response.text()}`)
    }

    return await response.json()
  }

  // Reports API request (POST)
  async reportsRequest(reportName: string, filters: any = {}) {
    const url = `https://${this.database}.appfolio.com/api/v2/reports/${reportName}.json`
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Basic ${this.reportsAuth}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(filters),
    })

    if (!response.ok) {
      throw new Error(`Reports API ${response.status}: ${await response.text()}`)
    }

    return await response.json()
  }

  // Handle pagination for Reports API
  async getAllReportData(reportName: string, filters: any = {}) {
    let allResults: any[] = []
    
    const data = await this.reportsRequest(reportName, filters)
    allResults = allResults.concat(data.results || data)
    let nextPageUrl = data.next_page_url

    while (nextPageUrl) {
      const response = await fetch(nextPageUrl, {
        method: 'POST',
        headers: {
          'Authorization': `Basic ${this.reportsAuth}`,
          'Content-Type': 'application/json',
        },
      })
      
      if (!response.ok) break
      
      const pageData = await response.json()
      allResults = allResults.concat(pageData.results || pageData)
      nextPageUrl = pageData.next_page_url
    }

    return { results: allResults }
  }
}

// Sync Functions
async function syncProperties(appfolio: AppFolioClient, supabase: any) {
  console.log('Syncing AF_Properties...')
  
  const data = await appfolio.stackRequest('properties')
  await supabase.from('AF_Properties').delete().neq('id', 0)
  
  const mapped = data.map((p: any) => ({
    PropertyId: p.Id,
    Name: p.Name,
    PropertyType: p.PropertyType,
    Address1: p.Address1,
    Address2: p.Address2,
    City: p.City,
    State: p.State,
    Zip: p.Zip,
    MaintenanceNotes: p.MaintenanceNotes,
    TenantPortalLink: p.TenantPortalLink,
    PropertyGroupIds: p.PropertyGroupIds,
    HiddenAt: p.HiddenAt,
    LastUpdatedAt: p.LastUpdatedAt,
    synced_at: new Date().toISOString(),
    sync_status: 'success'
  }))
  
  const { error } = await supabase.from('AF_Properties').insert(mapped)
  if (error) throw error
  
  console.log(`✓ Synced ${mapped.length} properties`)
  return { success: true, count: mapped.length }
}

async function syncPropertyGroups(appfolio: AppFolioClient, supabase: any) {
  console.log('Syncing AF_PropertyGroups...')
  
  const data = await appfolio.stackRequest('property_groups')
  await supabase.from('AF_PropertyGroups').delete().neq('id', 0)
  
  const mapped = data.map((pg: any) => ({
    PropertyGroupId: pg.Id,
    Name: pg.Name,
    Type: pg.Type,
    LastUpdatedAt: pg.LastUpdatedAt,
    synced_at: new Date().toISOString(),
    sync_status: 'success'
  }))
  
  const { error } = await supabase.from('AF_PropertyGroups').insert(mapped)
  if (error) throw error
  
  console.log(`✓ Synced ${mapped.length} property groups`)
  return { success: true, count: mapped.length }
}

async function syncBillDetail(appfolio: AppFolioClient, supabase: any) {
  console.log('Syncing AF_BillDetail...')
  
  const { results } = await appfolio.getAllReportData('bill_detail', {
    property_visibility: 'active'
  })
  
  await supabase.from('AF_BillDetail').delete().neq('id', 0)
  
  const mapped = results.map((b: any) => ({
    PayableInvoiceDetailID: b.payable_invoice_detail_id,
    TxnId: b.txn_id,
    ReferenceNumber: b.reference_number,
    BillDate: b.bill_date,
    DueDate: b.due_date,
    PostingDate: b.posting_date,
    // Add all other fields from your table
    synced_at: new Date().toISOString(),
    sync_status: 'success'
  }))
  
  const BATCH_SIZE = 1000
  for (let i = 0; i < mapped.length; i += BATCH_SIZE) {
    const batch = mapped.slice(i, i + BATCH_SIZE)
    const { error } = await supabase.from('AF_BillDetail').insert(batch)
    if (error) throw error
  }
  
  console.log(`✓ Synced ${mapped.length} bill detail records`)
  return { success: true, count: mapped.length }
}

// Main Handler
serve(async (req) => {
  try {
    const appfolio = new AppFolioClient(
      Deno.env.get('APPFOLIO_DATABASE')!,
      Deno.env.get('APPFOLIO_STACK_CLIENT_ID')!,
      Deno.env.get('APPFOLIO_STACK_CLIENT_SECRET')!,
      Deno.env.get('APPFOLIO_REPORTS_CLIENT_ID')!,
      Deno.env.get('APPFOLIO_REPORTS_CLIENT_SECRET')!
    )

    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    )

    const results = {
      properties: await syncProperties(appfolio, supabase),
      property_groups: await syncPropertyGroups(appfolio, supabase),
      bill_detail: await syncBillDetail(appfolio, supabase),
    }

    return new Response(
      JSON.stringify({ 
        success: true, 
        results,
        timestamp: new Date().toISOString()
      }),
      { status: 200, headers: { 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('Sync failed:', error)
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { status: 500, headers: { 'Content-Type': 'application/json' } }
    )
  }
})
```

### Step 8: Deploy and Test

```bash
# Set environment secrets
supabase secrets set APPFOLIO_DATABASE=stantonmgmt
supabase secrets set APPFOLIO_STACK_CLIENT_ID=your_id
supabase secrets set APPFOLIO_STACK_CLIENT_SECRET=your_secret
supabase secrets set APPFOLIO_REPORTS_CLIENT_ID=your_id
supabase secrets set APPFOLIO_REPORTS_CLIENT_SECRET=your_secret

# Deploy function
supabase functions deploy sync-appfolio

# Test it
supabase functions invoke sync-appfolio --no-verify-jwt

# Check logs
supabase functions logs sync-appfolio
```

### Step 9: Verify Data

```sql
-- Check synced data
SELECT COUNT(*) FROM "AF_Properties";
SELECT COUNT(*) FROM "AF_PropertyGroups";
SELECT COUNT(*) FROM "AF_BillDetail";

-- View sample data
SELECT * FROM "AF_Properties" LIMIT 5;
SELECT * FROM "AF_PropertyGroups" LIMIT 5;
SELECT * FROM "AF_BillDetail" LIMIT 5;
```

## Quick Reference: Common Endpoints

### Stack API (use these for buildings/portfolios)
| What You Want | Correct Endpoint |
|--------------|------------------|
| Buildings/Properties | `properties` |
| Portfolios | `property_groups` |
| Units | `units` |
| Tenants | `tenants` |
| Owners | `owners` |
| Vendors | `vendors` |

### Reports API (use these for financial reports)
| Report Type | Correct Endpoint |
|------------|------------------|
| Bills | `bill_detail.json` |
| Aged Receivables | `aged_receivables_detail.json` |
| Rent Roll | `rent_roll.json` |
| Work Orders | `work_order.json` |
| GL Accounts | `chart_of_accounts.json` |

## Troubleshooting Checklist

- [ ] Are you using the correct API (Stack vs Reports)?
- [ ] Did you quote all table and column names in SQL?
- [ ] Did you test the endpoint with curl/Postman first?
- [ ] Did you check the actual API response field names?
- [ ] Did you use the correct credentials for each API?
- [ ] Is your `id` field using `UUID DEFAULT gen_random_uuid()`?
- [ ] Did you map AppFolio field names correctly (PascalCase vs snake_case)?

## Key Takeaways

1. **Two different APIs**: Stack API for operational data, Reports API for reports
2. **Always quote names**: `"TableName"` and `"ColumnName"` to preserve case
3. **Test endpoints first**: Use curl or test script before creating tables
4. **Check field names**: Stack API uses PascalCase, Reports API uses snake_case
5. **Standard ID**: Always use `"id" UUID DEFAULT gen_random_uuid() PRIMARY KEY`