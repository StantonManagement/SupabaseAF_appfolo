import json

from .appfolio import get_appfolio_details
from .supabase_client import update_supabase_details


def sync_details(dataset: str):
    appfolio_results = get_appfolio_details(dataset)

    update_supabase_details(dataset, appfolio_results)

    # print(json.dumps(appfolio_results[0], indent=4))

    return appfolio_results
