import logging

from .appfolio import get_appfolio_details
from .supabase_client import update_supabase_details

# Create logger for this module
logger = logging.getLogger(__name__)


def sync_details(dataset: str):
    logger.info(f"INITIATING SYNC PROCESS FOR DATASET: '{dataset}'")

    # Get data from AppFolio API
    appfolio_results = get_appfolio_details(dataset)

    # Update Supabase and get sync statistics
    sync_result = update_supabase_details(dataset, appfolio_results)

    # Log the final results that will be returned to the API
    logger.info(f"SYNC PROCESS COMPLETED FOR DATASET '{dataset}'")

    return sync_result
