from .appfolio import get_bill_details
from .supabase_client import update_bill_details


def sync_bill_details():
    data = get_bill_details()
    update_bill_details(data)
