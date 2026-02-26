import logging
from supabase import create_client, Client
import os

from dotenv import load_dotenv
from ..helpers.constants import DETAILS, FIELD_MAP, ON_CONFLICT
from ..helpers.utils import clean_record

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Create logger for this module
logger = logging.getLogger(__name__)

# Validate required environment variables
if not url or not key:
    logger.error("�️ Missing required Supabase credentials in environment variables")
    raise ValueError("Missing required Supabase credentials in environment variables")

supabase: Client = create_client(url, key)


def update_supabase_details(dataset: str, appfolio_results):
    success_count = 0
    failed_count = 0

    total_records = len(appfolio_results)

    # Validate dataset exists in DETAILS mapping
    if dataset not in DETAILS:
        logger.error(
            f"⛔ Unsupported dataset '{dataset}'. Supported datasets: {', '.join(DETAILS.keys())}"
        )
        raise ValueError(
            f"Unsupported dataset '{dataset}'. Supported datasets: {', '.join(DETAILS.keys())}"
        )

    # Validate Supabase table exists
    if not DETAILS[dataset]:
        logger.error(f"📁 No Supabase table mapping found for dataset '{dataset}'")
        raise ValueError(f"No Supabase table mapping found for dataset '{dataset}'")

    logger.info(
        f"🚀 STARTING SYNC FOR DATASET '{dataset}' - TOTAL RECORDS TO PROCESS: {total_records}"
    )

    for i, record in enumerate(appfolio_results, 1):
        try:
            cleaned_record = clean_record(record)
            field_map = FIELD_MAP.get(dataset)
            if field_map:
                cleaned_record = {field_map[k]: v for k, v in cleaned_record.items() if k in field_map}
            conflict_col = ON_CONFLICT.get(dataset)
            query = supabase.table(DETAILS[dataset]).upsert(cleaned_record, on_conflict=conflict_col) if conflict_col else supabase.table(DETAILS[dataset]).upsert(cleaned_record)
            query.execute()
            success_count += 1
        except Exception as e:
            logger.error(f"💥 Error upserting record {i}/{total_records}: {e}")
            failed_count += 1

    failed_count = total_records - success_count

    # Log final results
    logger.info(f"✅ SYNC COMPLETE FOR DATASET '{dataset}':")
    logger.info(f"  - ✅ Success: {success_count}")
    logger.info(f"  - ❌ Failed: {failed_count}")
    logger.info(f"  - 📊 Total: {total_records}")

    return {"success": success_count, "failed": failed_count, "total": total_records}
