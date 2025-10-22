from supabase import create_client, Client
import os
import json

from dotenv import load_dotenv
from ..helpers.constants import DETAILS
from ..helpers.utils import clean_record

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(url, key)


def update_supabase_details(dataset: str, appfolio_results):
    print(appfolio_results)
    # print(DETAILS[dataset])

    # for record in appfolio_results:
    #     cleaned_record = clean_record(record)
    #     state = supabase.table(DETAILS[dataset]).upsert(cleaned_record).execute()
    #     print(state)
    #     print("=" * 60)

    print(len(appfolio_results))

    # fetched_dta = supabase.table(DETAILS[dataset]).select("*").execute()
    # print(fetched_dta)
