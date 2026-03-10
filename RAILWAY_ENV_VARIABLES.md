# Railway Environment Variables

Copy and paste these into Railway's **Raw Editor** in the Variables tab.

**IMPORTANT:**
- Do NOT include quotes around values
- Copy the ENTIRE line for each variable
- Make sure no line breaks in the middle of long keys

---

## Complete Environment Variables

```
SUPABASE_URL=https://wkwmxxlfheywwbgdbzxe.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indrd214eGxmaGV5d3diZ2RienhlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwOTcxOTIsImV4cCI6MjA3OTQ1NzE5Mn0.G4UyeP2BVuGG35oGDXMJcgbSCVVtBhSO6WddG-b6bm4
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indrd214eGxmaGV5d3diZ2RienhlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDA5NzE5MiwiZXhwIjoyMDc5NDU3MTkyfQ.niks8sCfMwsw704YW9fo7CNR9r3JddVCTbxCn-sVyrY
APPFOLIO_CLIENT_ID=7986fe0a73132b6dc3879bbc5d8ee4c8
APPFOLIO_CLIENT_SECRET=397b9c151d85dbe670075dddb8d8e29d
V1_BASE_URL=https://stantonmgmt.appfolio.com/api/v1
V2_BASE_URL=https://stantonmgmt.appfolio.com/api/v2/reports
```

---

## How to Use in Railway

1. Go to your **Work Orders Sync** service in Railway
2. Click on **Variables** tab
3. Click **Raw Editor** button
4. **Delete everything** in the editor
5. **Copy the entire block above** (from SUPABASE_URL to V2_BASE_URL)
6. **Paste** into Railway's Raw Editor
7. Click **Save**
8. Wait for service to restart (1-2 minutes)
9. Go to **Cron Runs** tab and click **Run now**
10. Check logs - should see success messages!

---

## Repeat for All 4 Services

You need to add these same variables to:
- ✅ Work Orders Sync
- ⚠️ Tenants Sync
- ⚠️ Units Sync
- ⚠️ Properties Sync

Use the same exact values for all services.

---

## Verification

After updating variables and running the cron, you should see in logs:

```
✅ SUCCESSFULLY FETCHED X RECORDS FROM APPFOLIO
✅ SYNC COMPLETE FOR DATASET 'work_order':
  - ✅ Success: X
  - ❌ Failed: 0
  - 📊 Total: X
✅ Updated sync state for 'work_order': X rows, status=success
```

**No more 401 errors!** 🎉
