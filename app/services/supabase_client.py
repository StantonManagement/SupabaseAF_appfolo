from supabase import create_client, Client
import os

from dotenv import load_dotenv
from ..helpers.constants import DETAILS
from ..helpers.utils import clean_record

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Validate required environment variables
if not url or not key:
    raise ValueError("Missing required Supabase credentials in environment variables")

supabase: Client = create_client(url, key)


def update_supabase_details(dataset: str, appfolio_results):
    success_count = 0
    failed_count = 0

    total_records = len(appfolio_results)

    # Validate dataset exists in DETAILS mapping
    if dataset not in DETAILS:
        raise ValueError(f"Unsupported dataset '{dataset}'. Supported datasets: {', '.join(DETAILS.keys())}")

    # Validate Supabase table exists
    if not DETAILS[dataset]:
        raise ValueError(f"No Supabase table mapping found for dataset '{dataset}'")

    for record in appfolio_results:
        try:
            cleaned_record = clean_record(record)
            supabase.table(DETAILS[dataset]).upsert(cleaned_record).execute()
            success_count += 1
        except Exception as e:
            print(f"Error upserting record: {e}")
            failed_count += 1

    failed_count = total_records - success_count

    return {
        "success": success_count,
        "failed": failed_count,
        "total": total_records
    }
