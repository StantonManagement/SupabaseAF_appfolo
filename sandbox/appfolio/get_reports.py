import logging
import requests
import os
import base64
import json

from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("APPFOLIO_CLIENT_ID")
CLIENT_SECRET = os.getenv("APPFOLIO_CLIENT_SECRET")
V1_BASE_URL = os.getenv("V1_BASE_URL")
V2_BASE_URL = os.getenv("V2_BASE_URL")

# Create logger for this module
logger = logging.getLogger(__name__)

credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()
headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/json",
}

reports = [
    "tenant_transactions_summary",
    "tenant_unpaid_charges_summary",
    "twelve_month_cash_flow",
    "unit_custom_fields",
    "unit_directory",
    "unit_inspection",
    "unpaid_balances_by_month",
    "upcoming_activities",
    "vendor_custom_fields",
    "vendor_directory",
    "vendor_ledger",
]

for dataset in reports:
    response = requests.post(f"{V2_BASE_URL}/{dataset}", headers=headers, timeout=30)
    print("FOR DATASET: ", dataset)

    try:
        data = response.json()
        print(json.dumps(data["results"][0], indent=2))
    except Exception as e:
        print(e)
        print("Cannot get data for dataset: ", dataset)

    print("-" * 20)
    print("\n\n\n")
