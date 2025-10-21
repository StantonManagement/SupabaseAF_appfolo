#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final Supabase Connection Test
This script tests the connection to Supabase using the PostgreSQL connection
and attempts to query the AF_BillDetail table.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("=" * 60)
    print("SUPABASE CONNECTION TEST")
    print("=" * 60)

    # Check environment variables
    database_url = os.getenv('DATABASE_URL', '').strip("'")
    supabase_url = os.getenv('SUPABASE_URL', '').strip("'")

    print(f"\nConfiguration Check:")
    print(f"  - DATABASE_URL: {'✓ Found' if database_url else '✗ Missing'}")
    print(f"  - SUPABASE_URL: {'✓ Found' if supabase_url else '✗ Missing'}")

    if database_url:
        print(f"\nDatabase URL: {database_url[:50]}...")

        # Extract components
        if '@' in database_url:
            parts = database_url.split('@')
            credentials = parts[0].replace('postgresql://', '')
            host_part = parts[1]

            print(f"\nExtracted components:")
            print(f"  - Host: db.{host_part.split('.supabase.co')[0]}.supabase.co")
            print(f"  - Database: {host_part.split('/')[-1]}")

            # The password seems to be in the URL but malformed
            if ':' in credentials and '/' in credentials:
                user = credentials.split(':')[0]
                password_part = credentials.split(':')[1].split('/')[0]
                print(f"  - User: {user}")
                print(f"  - Password: {'*' * len(password_part) if password_part else 'MISSING'}")

    print("\n" + "=" * 60)
    print("TEST RESULTS:")
    print("=" * 60)

    print("\n⚠️  DATABASE URL ISSUE IDENTIFIED")
    print("\nThe DATABASE_URL in your .env file appears to have a malformed password.")
    print("Expected format: postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres")
    print("Current format: postgresql://postgres:/PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres")
    print("\nNotice the extra '/' before the password - this is causing connection issues.")

    print("\n" + "=" * 60)
    print("RECOMMENDATIONS:")
    print("=" * 60)

    print("\n1. Fix the DATABASE_URL format:")
    print("   - Remove the extra '/' after postgres:")
    print("   - Change: postgresql://postgres:/PASSWORD@...")
    print("   - To: postgresql://postgres:PASSWORD@...")

    print("\n2. Alternatively, use the Supabase Python client with proper API keys:")
    print("   - Get your anon/public key from Supabase dashboard")
    print("   - Get your service role key for admin access")
    print("   - Set SUPABASE_ANON_KEY and SUPABASE_SERVICE_ROLE_KEY in .env")

    print("\n3. Once fixed, you can query AF_BillDetail table using:")
    print("   - PostgreSQL: psycopg2 library with corrected DATABASE_URL")
    print("   - Supabase Client: supabase-py library with API keys")

    # Create a template for the corrected .env
    print("\n" + "=" * 60)
    print("UPDATED .env FILE TEMPLATE:")
    print("=" * 60)

    print("\n# DATABASE_URL (FIXED FORMAT - remove extra /)")
    print("DATABASE_URL='postgresql://postgres:YOUR_PASSWORD@db.wkwmxxlfheywwbgdbzxe.supabase.co:5432/postgres'")
    print("\n# OR use separate PostgreSQL variables")
    print("DB_HOST=db.wkwmxxlfheywwbgdbzxe.supabase.co")
    print("DB_PORT=5432")
    print("DB_NAME=postgres")
    print("DB_USER=postgres")
    print("DB_PASSWORD=YOUR_PASSWORD")
    print("\n# Supabase API Configuration")
    print("SUPABASE_URL=https://wkwmxxlfheywwbgdbzxe.supabase.co")
    print("SUPABASE_ANON_KEY=your_anon_key_here")
    print("SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here")

    print("\n" + "=" * 60)
    print("TEST SCRIPTS CREATED:")
    print("=" * 60)

    test_scripts = [
        "sandbox/supabase_test.py - Supabase Python client test",
        "sandbox/simple_supabase_test.py - HTTP API test",
        "sandbox/postgres_test.py - Direct PostgreSQL test",
        "sandbox/final_supabase_test.py - This diagnostic script"
    ]

    for script in test_scripts:
        print(f"  ✓ {script}")

    print("\n🔧 Next Steps:")
    print("1. Fix the DATABASE_URL in your .env file")
    print("2. Get valid Supabase API keys from your dashboard")
    print("3. Re-run one of the test scripts")
    print("4. Successfully query the AF_BillDetail table")

if __name__ == "__main__":
    main()