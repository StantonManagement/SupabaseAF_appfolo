#!/usr/bin/env python3
"""
Quick audit script to check AF table status
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(url, key)

print("\n" + "="*80)
print("QUICK AF TABLES AUDIT")
print("="*80 + "\n")

# Query 1: Row counts for main tables
print("📊 ROW COUNTS:")
print("-" * 80)

tables = [
    ("AF_WorkOrder", 1000, 10000),
    ("AF_TenantDirectory", 1000, 10000),
    ("AF_UnitDirectory", 1000, 10000),
    ("AF_buildings", 500, 5000),
]

total_rows = 0
for table_name, good_threshold, monitor_threshold in tables:
    try:
        result = supabase.table(table_name).select("*", count="exact").execute()
        count = result.count
        total_rows += count

        if count < good_threshold:
            status = "✅ Good"
        elif count < monitor_threshold:
            status = "⚠️ Monitor"
        else:
            status = "❌ Bloated"

        print(f"{table_name:30} {count:>6} rows    {status}")
    except Exception as e:
        print(f"{table_name:30} ERROR: {e}")

print(f"\n{'📊 TOTAL (all above)':30} {total_rows:>6} rows")
print()

# Query 2: Sync state
print("\n📅 SYNC STATE:")
print("-" * 80)

try:
    sync_state = supabase.table("appfolio_sync_state").select("*").order("last_synced_at", desc=True).execute()

    if sync_state.data:
        for row in sync_state.data:
            endpoint = row.get("endpoint", "Unknown")
            last_synced = row.get("last_synced_at", "Never")
            status = row.get("last_run_status", "Unknown")
            row_count = row.get("last_row_count", 0)

            # Determine freshness
            if "1970-01-01" in str(last_synced) or "1971-01-01" in str(last_synced):
                freshness = "⚪ Never"
            elif "2026-03-09" in str(last_synced):
                freshness = "🟢 Today"
            else:
                freshness = "🔴 Old"

            print(f"{endpoint:30} {last_synced:25} {status:10} {row_count:>6} rows  {freshness}")
    else:
        print("No sync state records found")
except Exception as e:
    print(f"ERROR: {e}")

print("\n" + "="*80)
print("AUDIT COMPLETE")
print("="*80 + "\n")
