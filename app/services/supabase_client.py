from supabase import create_client, Client
import os

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(url, key)


def update_bill_details(data):
    print("THIS IS THE DATA FROM SUPABASE")
    print(data)
    # for record in data:
    #     supabase.table("bill_detail").upsert(record).execute()
