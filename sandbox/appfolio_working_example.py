"""
AppFolio API Integration - Working Example with Troubleshooting

This script provides a working template for AppFolio API integration.
It includes comprehensive error handling and troubleshooting guidance.

IMPORTANT: Before running this script, ensure:
1. Your AppFolio account has API access enabled
2. You have valid client credentials from AppFolio
3. Your IP address is whitelisted if required
4. The subdomain 'stantonmgmt' is correct for your account

To get API access:
1. Contact AppFolio support to enable API access for your account
2. Request client credentials (CLIENT_ID and CLIENT_SECRET)
3. Ensure your account has the necessary permissions for the endpoints you need

Troubleshooting steps:
- If you get 404 errors: Your account likely doesn't have API access enabled
- If you get 401 errors: Your credentials are invalid or expired
- If you get connection errors: Check your subdomain and network connectivity
"""

import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class AppFolioAPI:
    def __init__(self, subdomain, client_id=None, client_secret=None):
        """
        Initialize AppFolio API client

        Args:
            subdomain (str): Your AppFolio subdomain (e.g., 'mycompany')
            client_id (str): OAuth client ID
            client_secret (str): OAuth client secret
        """
        self.subdomain = subdomain
        self.client_id = client_id or os.getenv("APPFOLIO_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("APPFOLIO_CLIENT_SECRET")
        self.access_token = None
        self.token_expires_at = None

        # API base URLs - try multiple patterns
        self.api_bases = [
            f"https://{subdomain}.appfolio.com",  # Subdomain-specific
            "https://api.appfolio.com",           # API gateway
        ]

        # OAuth endpoints to try
        self.oauth_endpoints = [
            f"https://{subdomain}.appfolio.com/oauth/token",  # Subdomain OAuth
            "https://api.appfolio.com/oauth2/token",          # API gateway OAuth
        ]

        # API endpoints
        self.endpoints = {
            "charges": "/api/v1/charges",
            "leases": "/api/v1/leases",
            "owners": "/api/v1/owners",
            "vendors": "/api/v1/vendors",
            "properties": "/api/v1/properties",
            "units": "/api/v1/units",
            "residents": "/api/v1/residents",
            "journal_entries": "/api/v1/journal_entries",
            "invoices": "/api/v1/invoices",
            "payments": "/api/v1/payments"
        }

    def get_access_token(self):
        """
        Get OAuth access token using client credentials flow

        Returns:
            str: Access token or None if authentication fails
        """
        if not self.client_id or not self.client_secret:
            raise ValueError("Client ID and Client Secret are required")

        auth_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }

        # Try each OAuth endpoint
        for oauth_url in self.oauth_endpoints:
            try:
                print(f"Attempting OAuth at: {oauth_url}")
                response = requests.post(oauth_url, data=auth_data, headers=headers, timeout=30)

                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data.get("access_token")
                    expires_in = token_data.get("expires_in", 3600)

                    # Set token expiration time
                    self.token_expires_at = datetime.now().timestamp() + expires_in - 60  # 1 minute buffer

                    print(f"✓ Successfully obtained access token")
                    return self.access_token

                else:
                    print(f"✗ OAuth failed at {oauth_url}: {response.status_code}")
                    if response.status_code != 404:  # Only show response for non-404 errors
                        print(f"Response: {response.text}")

            except requests.exceptions.RequestException as e:
                print(f"✗ Request error at {oauth_url}: {str(e)}")

        return None

    def make_request(self, method, endpoint, params=None, data=None):
        """
        Make authenticated API request

        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint path
            params (dict): Query parameters
            data (dict): Request body data

        Returns:
            dict: Response data or None if request fails
        """
        # Get access token if we don't have one or it's expired
        if not self.access_token or (self.token_expires_at and datetime.now().timestamp() > self.token_expires_at):
            if not self.get_access_token():
                raise Exception("Failed to obtain access token")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # Try each API base URL
        for base_url in self.api_bases:
            url = f"{base_url}{endpoint}"

            try:
                print(f"Making {method} request to: {url}")

                if method.upper() == "GET":
                    response = requests.get(url, headers=headers, params=params, timeout=30)
                elif method.upper() == "POST":
                    response = requests.post(url, headers=headers, json=data, timeout=30)
                elif method.upper() == "PUT":
                    response = requests.put(url, headers=headers, json=data, timeout=30)
                elif method.upper() == "DELETE":
                    response = requests.delete(url, headers=headers, timeout=30)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    print("Token may be expired, refreshing...")
                    self.access_token = None
                    return self.make_request(method, endpoint, params, data)
                else:
                    print(f"Request failed: {response.status_code}")
                    print(f"Response: {response.text}")

            except requests.exceptions.RequestException as e:
                print(f"Request error: {str(e)}")
                continue

        return None

    def get_charges(self, limit=10):
        """
        Get charges from AppFolio

        Args:
            limit (int): Maximum number of charges to retrieve

        Returns:
            list: List of charges or None if request fails
        """
        params = {"limit": limit}
        return self.make_request("GET", self.endpoints["charges"], params=params)

    def get_leases(self, limit=10):
        """
        Get leases from AppFolio

        Args:
            limit (int): Maximum number of leases to retrieve

        Returns:
            list: List of leases or None if request fails
        """
        params = {"limit": limit}
        return self.make_request("GET", self.endpoints["leases"], params=params)

    def create_mock_charge(self):
        """
        Create a mock charge for testing purposes
        This simulates what a real charge response would look like
        """
        return {
            "id": "charge_123456",
            "lease_id": "lease_789012",
            "resident_id": "resident_345678",
            "property_id": "prop_901234",
            "unit_id": "unit_567890",
            "charge_type": "rent",
            "amount": 1500.00,
            "due_date": "2024-02-01",
            "description": "Monthly Rent - February 2024",
            "status": "pending",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }

def test_appfolio_api():
    """
    Test function demonstrating how to use the AppFolio API client
    """
    print("AppFolio API Test")
    print("="*50)

    # Initialize API client
    api = AppFolioAPI("stantonmgmt")

    # Check if credentials are present
    if not api.client_id or not api.client_secret:
        print("✗ ERROR: Missing credentials")
        print("Please set APPFOLIO_CLIENT_ID and APPFOLIO_CLIENT_SECRET environment variables")
        print("Or pass them directly to the AppFolioAPI constructor")
        return False

    print(f"✓ Credentials loaded")
    print(f"  Client ID: {api.client_id[:10]}...")
    print(f"  Subdomain: {api.subdomain}")

    # Try to get charges
    print("\nAttempting to fetch charges...")
    try:
        charges = api.get_charges(limit=5)

        if charges:
            print(f"✓ Success! Found {len(charges)} charges")
            for i, charge in enumerate(charges[:3], 1):
                print(f"  {i}. {charge}")
            return True
        else:
            print("✗ Failed to fetch charges")

            # Show mock data for reference
            print("\nHere's what a successful charge response would look like:")
            mock_charge = api.create_mock_charge()
            print(json.dumps(mock_charge, indent=2))

            return False

    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_appfolio_api()

    if not success:
        print("\n" + "="*50)
        print("TROUBLESHOOTING GUIDE")
        print("="*50)
        print("1. Ensure API access is enabled for your AppFolio account")
        print("2. Verify your client credentials are correct and active")
        print("3. Check that your subdomain 'stantonmgmt' is correct")
        print("4. Contact AppFolio support for API access if needed")
        print("5. Review AppFolio API documentation for any updates")
        print("\nCommon solutions:")
        print("- Request API access from AppFolio support")
        print("- Regenerate your client credentials")
        print("- Verify your account has the necessary permissions")
        print("- Check if your IP needs to be whitelisted")