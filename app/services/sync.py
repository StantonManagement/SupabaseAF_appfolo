from .appfolio import get_appfolio_details
from .supabase_client import update_supabase_details


def sync_details(dataset: str):
    data = get_appfolio_details(dataset)
    update_supabase_details(dataset, data)

    return data
