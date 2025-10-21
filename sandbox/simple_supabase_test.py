#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Extract from DATABASE_URL if SUPABASE_URL not available
DATABASE_URL = os.getenv('DATABASE_URL', '')
if DATABASE_URL and not os.getenv('SUPABASE_URL'):
    # Extract project URL from DATABASE_URL
    # postgresql://postgres:password@db.wkwmxxlfheywwbgdbzxe.supabase.co:5432/postgres
    if '@db.' in DATABASE_URL:
        project_id = DATABASE_URL.split('@db.')[1].split('.supabase.co')[0]
        SUPABASE_URL = f"https://{project_id}.supabase.co"
    else:
        SUPABASE_URL = 'https://rpjvxfgodkwwbgukkrya.supabase.co'
else:
    SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

print("=== Simple Supabase Connection Test ===")
print(f"URL: {SUPABASE_URL}")
print(f"Anon Key exists: {bool(SUPABASE_ANON_KEY)}")
print(f"Service Role Key exists: {bool(SUPABASE_SERVICE_ROLE_KEY)}")

# Test HTTP connection
print("\nTesting HTTP connection...")
headers = {
    'apikey': SUPABASE_ANON_KEY,
    'Authorization': f'Bearer {SUPABASE_ANON_KEY}'
}

try:
    response = httpx.get(f"{SUPABASE_URL}/rest/v1/", headers=headers, timeout=10)
    print(f"HTTP Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Basic HTTP connection successful")
    else:
        print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"❌ HTTP connection failed: {e}")

# Test if we can list tables
print("\nAttempting to list tables...")
try:
    # Try to get schema information
    response = httpx.get(
        f"{SUPABASE_URL}/rest/v1/",
        headers=headers,
        params={'select': '*'},
        timeout=10
    )
    print(f"Schema response status: {response.status_code}")
except Exception as e:
    print(f"❌ Schema query failed: {e}")

# Test AF_BillDetail table specifically
print("\nTesting AF_BillDetail table...")
try:
    response = httpx.get(
        f"{SUPABASE_URL}/rest/v1/AF_BillDetail",
        headers=headers,
        params={'select': '*', 'limit': '1'},
        timeout=10
    )
    print(f"AF_BillDetail query status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ AF_BillDetail table accessible!")
        print(f"Sample data: {data[:1] if data else 'No data'}")
    else:
        print(f"Error response: {response.text[:200]}")
except Exception as e:
    print(f"❌ AF_BillDetail query failed: {e}")

print("\n=== Test Complete ===")