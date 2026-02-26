# Buildings API Fix - Session Notes

**Date:** February 25-26, 2026
**Status:** ✅ Fixed and Committed Locally (Not Pushed Yet)

## Problem Summary

The `AF_Buildings` table in Supabase was not syncing from AppFolio:
- **Last successful sync:** January 16, 2026 (over a month ago)
- **Root cause:** Old Stack API credentials no longer available
- **Current credentials:** Reports API only (doesn't have direct "buildings" endpoint)

## Solution Implemented

Created a **field transformation system** that:
1. Fetches property data from `property_group_directory` (Reports API v2)
2. Transforms field names to match `AF_Buildings` table schema
3. Successfully syncs 272 buildings

## Files Modified

### 1. `app/helpers/utils.py`
- Added `transform_property_to_building()` function
- Maps AppFolio fields → AF_Buildings columns
- Handles field type conversions (portfolio_id → Portfolio as integer)

### 2. `app/helpers/constants.py`
- Added `"buildings": "AF_Buildings"` mapping
- Added `DATASET_TRANSFORMATIONS` config

### 3. `app/services/appfolio.py`
- Checks for dataset transformations
- Fetches from correct source (property_group_directory)

### 4. `app/services/supabase_client.py`
- Applies transformation before upserting to Supabase

## Test Results

```bash
# Test command:
curl -X POST http://localhost:8000/sync_details \
  -H 'Content-Type: application/json' \
  -d '{"dataset": "buildings"}'

# Result:
{"success":272,"failed":0,"total":272}
```

✅ All 272 buildings synced successfully
✅ Data correctly mapped to AF_Buildings table
✅ last_synced timestamps updated to Feb 26, 2026

## How to Use

### Sync Buildings Locally
```bash
curl -X POST http://localhost:8000/sync_details \
  -H 'Content-Type: application/json' \
  -d '{"dataset": "buildings"}'
```

### Sync Buildings in Production (Railway)
```bash
curl -X POST https://supabaseafappfolo-production.up.railway.app/sync_details \
  -H 'Content-Type: application/json' \
  -d '{"dataset": "buildings"}'
```

## Git Status

**Commit:** `d5922dd feat: add buildings dataset with property transformation`
**Branch:** main (2 commits ahead of origin/main)
**Status:** Committed locally, NOT pushed yet

### To Push Changes:
```bash
git push origin main
```

## Environment Variables (Already Configured Locally)

`.env` file is configured with:
- ✅ SUPABASE_URL
- ✅ SUPABASE_SERVICE_ROLE_KEY
- ✅ APPFOLIO_CLIENT_ID
- ✅ APPFOLIO_CLIENT_SECRET
- ✅ V1_BASE_URL
- ✅ V2_BASE_URL

### For Railway Production:
Make sure these environment variables are set in Railway dashboard:
```
APPFOLIO_CLIENT_ID=7986fe0a73132b6dc3879bbc5d8ee4c8
APPFOLIO_CLIENT_SECRET=397b9c151d85dbe670075dddb8d8e29d
SUPABASE_URL=https://wkwmxxlfheywwbgdbzxe.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
V1_BASE_URL=https://stantonmgmt.appfolio.com/api/v1
V2_BASE_URL=https://stantonmgmt.appfolio.com/api/v2/reports
```

## Field Mapping Details

### property_group_directory → AF_Buildings

| AppFolio Field | AF_Buildings Column | Notes |
|----------------|---------------------|-------|
| property_name | PropertyName | String |
| property_address | PropertyAddress | String |
| property_city | PropertyCity | String |
| property_state | PropertyState | String |
| property_id | PropertyId | Integer |
| property_street | PropertyStreet1 | String |
| property_zip | PropertyZip | String |
| portfolio_id | Portfolio | **Integer** (was string before) |
| portfolio_id | PortfolioId | Integer |
| property_group_name | PropertyGroupName | String |
| property_group_id | PropertyGroupId | Integer |

**Building fields set to NULL:**
- BuildingName, BuildingId, BuildingAddress, BuildingStreet1, BuildingStreet2, BuildingCity, BuildingState, BuildingZip
- Units, SqFt, YearBuilt, PropertyType, BuildingType, Amenities, Description
- MarketRent, ManagementFeePercent, ManagementFlatFee, MinimumFee, MaximumFee

## Benefits of This Approach

✅ **No Stack API credentials needed** - Works with Reports API
✅ **Automatic transformation** - Handles field mapping automatically
✅ **Scalable** - Can reuse this pattern for other datasets
✅ **Backward compatible** - Existing datasets still work
✅ **Permanent fix** - Will continue working with current credentials

## Next Steps

1. **Test in production** after pushing to Railway
2. **Set up scheduled sync** for buildings dataset in Railway
3. **Monitor sync logs** for any errors
4. **Consider adding other transformations** using the same pattern

## Notes

- The transformation system uses `DATASET_TRANSFORMATIONS` config in `constants.py`
- Any dataset in this config will automatically fetch from the specified source and apply transformation
- The `appfolio_collection` field is set to "property_group_directory" to track the source

## Contact

**Fixed by:** Claude Code
**Session Date:** February 25-26, 2026
**Commit:** d5922dd
