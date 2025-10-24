from .appfolio import get_appfolio_details
from .supabase_client import update_supabase_details


def sync_details(dataset: str):
    # Get data from AppFolio API
    appfolio_results = get_appfolio_details(dataset)

    # Update Supabase and get sync statistics
    sync_result = update_supabase_details(dataset, appfolio_results)

    return sync_result
