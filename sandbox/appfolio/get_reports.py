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
    "occupancy_custom_fields",
    "occupancy_summary",
    "owner_custom_fields",
    "payment_plans",
    "premium_listing_billing_detail",
    "project_budget_detail",
    "project_directory",
    "property_budget",
    "property_custom_fields",
    "property_staff_assignments",
    "prospect_source_tracking",
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
