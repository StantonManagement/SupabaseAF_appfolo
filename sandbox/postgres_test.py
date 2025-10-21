#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

def test_postgres_connection():
    """Test direct PostgreSQL connection to Supabase and query AF_BillDetail table"""

    print("=== PostgreSQL Connection Test to Supabase ===\n")

    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not found in environment variables")
        return False

    # The DATABASE_URL has single quotes, remove them
    database_url = database_url.strip("'")
    print(f"Database URL found (length: {len(database_url)})")

    try:
        # Parse the database URL
        parsed = urlparse(database_url)

        # Extract connection parameters
        db_config = {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path[1:],  # Remove leading slash
            'user': parsed.username,
            'password': parsed.password
        }

        print(f"Connecting to PostgreSQL at {db_config['host']}:{db_config['port']}")
        print(f"Database: {db_config['database']}")
        print(f"User: {db_config['user']}\n")

        # Connect to the database
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        print("✅ PostgreSQL connection established successfully!\n")

        # Test 1: Check if AF_BillDetail table exists
        print("📋 Checking for AF_BillDetail table...")
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'AF_BillDetail'
            );
        """)
        table_exists = cursor.fetchone()[0]

        if table_exists:
            print("✅ AF_BillDetail table exists!\n")

            # Get table schema
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'AF_BillDetail'
                AND table_schema = 'public'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()

            print("📊 Table Schema:")
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                print(f"  - {col[0]}: {col[1]} ({nullable})")
            print()

        else:
            print("❌ AF_BillDetail table not found")

            # List all tables in the database
            print("\n📋 Available tables in public schema:")
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            for table in tables:
                print(f"  - {table[0]}")
            return False

        # Test 2: Query AF_BillDetail data
        print("🔍 Querying AF_BillDetail data...")
        cursor.execute("SELECT COUNT(*) FROM AF_BillDetail")
        total_rows = cursor.fetchone()[0]
        print(f"Total rows in AF_BillDetail: {total_rows:,}\n")

        if total_rows > 0:
            # Get first 10 records
            cursor.execute("""
                SELECT * FROM AF_BillDetail
                LIMIT 10
            """)
            records = cursor.fetchall()

            # Get column names
            column_names = [desc[0] for desc in cursor.description]

            # Create DataFrame for better display
            df = pd.DataFrame(records, columns=column_names)

            print(f"📊 Sample data (first {len(df)} records):")
            print(df.to_string(index=False, max_cols=10))

            # Show basic statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                print(f"\n📈 Statistics for numeric columns:")
                print(df[numeric_cols].describe())

            # Check for common columns
            common_cols = ['id', 'created_at', 'updated_at', 'amount', 'description', 'date']
            found_cols = [col for col in common_cols if col in df.columns]
            if found_cols:
                print(f"\n🔍 Found common columns: {found_cols}")

        # Test 3: Test a filtered query
        if total_rows > 0:
            print("\n🔍 Testing filtered query...")

            # Try different date columns
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'AF_BillDetail'
                AND table_schema = 'public'
                AND lower(column_name) LIKE '%date%'
                OR lower(column_name) LIKE '%time%'
                OR lower(column_name) LIKE '%created%'
                OR lower(column_name) LIKE '%updated%'
            """)
            date_cols = [row[0] for row in cursor.fetchall()]

            if date_cols:
                print(f"Found date-related columns: {date_cols}")

                # Try to get recent records
                date_col = date_cols[0]
                try:
                    cursor.execute(f"""
                        SELECT COUNT(*)
                        FROM AF_BillDetail
                        WHERE {date_col} >= NOW() - INTERVAL '30 days'
                    """)
                    recent_count = cursor.fetchone()[0]
                    print(f"Records in last 30 days: {recent_count:,}")

                    if recent_count > 0:
                        cursor.execute(f"""
                            SELECT * FROM AF_BillDetail
                            WHERE {date_col} >= NOW() - INTERVAL '30 days'
                            LIMIT 5
                        """)
                        recent_records = cursor.fetchall()
                        recent_df = pd.DataFrame(recent_records, columns=column_names)
                        print("\n📊 Recent records:")
                        print(recent_df.to_string(index=False, max_cols=8))

                except Exception as date_error:
                    print(f"⚠️ Date filtering failed: {date_error}")

            # Try to get some aggregated data
            try:
                cursor.execute("""
                    SELECT
                        COUNT(*) as total_count,
                        MIN(created_at) as earliest_record,
                        MAX(created_at) as latest_record
                    FROM AF_BillDetail
                    WHERE created_at IS NOT NULL
                """)
                stats = cursor.fetchone()
                if stats and stats[0] > 0:
                    print(f"\n📊 Table Statistics:")
                    print(f"  - Total records: {stats[0]:,}")
                    print(f"  - Earliest record: {stats[1]}")
                    print(f"  - Latest record: {stats[2]}")
            except:
                pass  # Ignore if created_at doesn't exist

        # Close connection
        cursor.close()
        conn.close()
        print("\n✅ Connection closed successfully")

        print("\n🎉 All tests completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Connection or query failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check if DATABASE_URL is correct")
        print("2. Ensure the Supabase project is active")
        print("3. Verify network connectivity")
        print("4. Check if the database credentials are valid")
        return False

if __name__ == "__main__":
    success = test_postgres_connection()
    if success:
        print("\n✅ PostgreSQL connection test PASSED!")
    else:
        print("\n❌ PostgreSQL connection test FAILED!")