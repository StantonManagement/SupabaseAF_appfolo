import logging

from .appfolio import get_appfolio_details
from .supabase_client import update_supabase_details, get_last_sync_time

# Create logger for this module
logger = logging.getLogger(__name__)


def sync_details(dataset: str, use_delta: bool = True):
    logger.info(f"⚡ INITIATING SYNC PROCESS FOR DATASET: '{dataset}'")

    # Get last sync time if delta sync is enabled
    last_synced_at = None
    if use_delta:
        last_synced_at = get_last_sync_time(dataset)
        if last_synced_at:
            logger.info(f"📅 Last sync: {last_synced_at} - Using DELTA sync")
        else:
            logger.info(f"📅 No previous sync found - Using FULL sync")

    # Get data from AppFolio API (with optional date filter)
    appfolio_results = get_appfolio_details(dataset, last_synced_at)

    # Update Supabase and get sync statistics
    sync_result = update_supabase_details(dataset, appfolio_results)

    # Log the final results that will be returned to the API
    logger.info(f"🎉 SYNC PROCESS COMPLETED FOR DATASET '{dataset}'")

    return sync_result
