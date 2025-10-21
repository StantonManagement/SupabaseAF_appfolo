from supabase import create_client, Client
import os

from dotenv import load_dotenv
from ..helpers.constants import DETAILS

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(url, key)


def update_supabase_details(dataset: str, data):
    print("THIS IS THE DATA FROM SUPABASE")
    print(data)
    print(DETAILS[dataset])
    # for record in data:
    #     supabase.table(DETAILS[dataset]).upsert(record).execute()
