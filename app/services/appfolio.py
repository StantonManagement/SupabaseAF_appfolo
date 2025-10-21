import requests
import os
import base64

CLIENT_ID = os.getenv("APPFOLIO_CLIENT_ID")
CLIENT_SECRET = os.getenv("APPFOLIO_CLIENT_SECRET")
BASE_URL = os.getenv("BASE_URL")

credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()
headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/json",
}

table = "bill_detail"
url = f"{BASE_URL}{table}"


def get_bill_details():
    print("THIS IS THE DATA FROM APPFOLIO")
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    data = response.json()
    results_count = len(data.get("results", []))

    return data["results"][0]
