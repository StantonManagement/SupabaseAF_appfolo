import requests
import os
import base64

from dotenv import load_dotenv
from ..helpers.constants import v1_dataset

load_dotenv()

CLIENT_ID = os.getenv("APPFOLIO_CLIENT_ID")
CLIENT_SECRET = os.getenv("APPFOLIO_CLIENT_SECRET")
V1_BASE_URL = os.getenv("V1_BASE_URL")
V2_BASE_URL = os.getenv("V2_BASE_URL")

credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()
headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/json",
}


def get_appfolio_details(dataset: str):
    print("THIS IS THE DATA FROM APPFOLIO")

    if dataset in v1_dataset:
        response = requests.get(f"{V1_BASE_URL}/{dataset}", headers=headers, timeout=30)
    else:
        response = requests.post(
            f"{V2_BASE_URL}/{dataset}", headers=headers, timeout=30
        )
    response.raise_for_status()

    data = response.json()
    return data["results"]
