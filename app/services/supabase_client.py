import logging
from supabase import create_client, Client
import os

from dotenv import load_dotenv
from ..helpers.constants import DETAILS, DATASET_TRANSFORMATIONS
from ..helpers.utils import clean_record, transform_property_to_building

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


def get_last_sync_time(dataset: str):
    """
    Get the last successful sync timestamp for a dataset.
    Returns ISO format timestamp string or None if never synced.
    """
    try:
        result = supabase.rpc("get_last_sync_time", {"p_endpoint": dataset}).execute()

        if result.data:
            logger.info(f"📅 Last sync for '{dataset}': {result.data}")
            return result.data
        else:
            logger.info(f"📅 No previous sync found for '{dataset}'")
            return None
    except Exception as e:
        logger.warning(f"⚠️ Could not get last sync time for '{dataset}': {e}")
        return None


def update_sync_state(dataset: str, row_count: int, status: str = "success"):
    """
    Update the sync state after a sync operation.
    """
    try:
        supabase.rpc(
            "update_sync_state",
            {
                "p_endpoint": dataset,
                "p_row_count": row_count,
                "p_status": status
            }
        ).execute()
        logger.info(f"✅ Updated sync state for '{dataset}': {row_count} rows, status={status}")
    except Exception as e:
        logger.error(f"❌ Failed to update sync state for '{dataset}': {e}")


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
            # Apply transformation if needed
            if dataset in DATASET_TRANSFORMATIONS:
                transform_func_name = DATASET_TRANSFORMATIONS[dataset]["transform"]
                if transform_func_name == "transform_property_to_building":
                    record = transform_property_to_building(record)
                    logger.debug(f"🔄 Applied transformation for record {i}")

            cleaned_record = clean_record(record)
            supabase.table(DETAILS[dataset]).upsert(cleaned_record).execute()
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

    # Update sync state in database
    sync_status = "success" if failed_count == 0 else "partial"
    update_sync_state(dataset, success_count, sync_status)

    return {"success": success_count, "failed": failed_count, "total": total_records}
