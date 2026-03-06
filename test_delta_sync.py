"""
Test script to verify delta sync implementation works
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.supabase_client import get_last_sync_time, update_sync_state

print("=" * 70)
print("TESTING DELTA SYNC INFRASTRUCTURE")
print("=" * 70)

# Test 1: Get last sync time (should return None for never-synced endpoint)
print("\n📋 Test 1: Get last sync time for new endpoint")
print("-" * 70)
result = get_last_sync_time("test_endpoint_12345")
print(f"Result: {result}")
print(f"✅ PASS" if result is None else f"❌ FAIL: Expected None, got {result}")

# Test 2: Update sync state
print("\n📋 Test 2: Update sync state")
print("-" * 70)
update_sync_state("test_endpoint_12345", 100, "success")
print("✅ Sync state updated")

# Test 3: Get last sync time again (should return timestamp now)
print("\n📋 Test 3: Get last sync time after update")
print("-" * 70)
result = get_last_sync_time("test_endpoint_12345")
print(f"Result: {result}")
print(f"✅ PASS" if result is not None else f"❌ FAIL: Expected timestamp, got None")

# Test 4: Check if work_order has been synced before
print("\n📋 Test 4: Check work_order sync state")
print("-" * 70)
result = get_last_sync_time("work_order")
print(f"Last synced: {result}")
if result:
    print("✅ work_order has been synced before (delta sync will work)")
else:
    print("ℹ️  work_order has never been synced (first run will be full sync)")

print("\n" + "=" * 70)
print("TESTS COMPLETE")
print("=" * 70)
print("\nNext steps:")
print("1. Run: python jobs/sync_work_orders.py")
print("2. Check logs for 'DELTA SYNC' or 'FULL SYNC' message")
print("3. Run again and verify it says 'DELTA SYNC'")
