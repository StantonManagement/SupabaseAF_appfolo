"""
AppFolio API Example - Using Environment Variables
Demonstrates secure credential management with .env file
"""

import requests
import base64
import time
import json
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class AppFolioAPI:
    """Client for interacting with AppFolio API"""

    def __init__(
        self, client_id: str = None, client_secret: str = None, base_url: str = None
    ):
        """
        Initialize AppFolio API client

        Args:
            client_id: AppFolio API client ID (defaults to env var)
            client_secret: AppFolio API client secret (defaults to env var)
            base_url: Base URL for API (defaults to stantonmgmt.appfolio.com)
        """
        self.client_id = client_id or os.getenv("APPFOLIO_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("APPFOLIO_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "AppFolio credentials not found. Set APPFOLIO_CLIENT_ID and APPFOLIO_CLIENT_SECRET"
            )

        self.base_url = base_url or "https://stantonmgmt.appfolio.com/api/v1/reports/"

        # Create Basic Auth header
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
        }

        # Endpoint mappings for all requested resources
        self.endpoints = {
            # Properties & Units
            "Properties": "property_directory.json",
            "PropertyGroups": "property_group_directory.json",
            "Units": "unit_directory.json",
            # Tenants & Leases
            "Tenants": "tenant_directory.json",
            "Leases": "lease_history.json",
            "RentalApplications": "rental_applications.json",
            # Owners
            "Owners": "owner_directory.json",
            # Financial - Bills & Charges
            "Bills": "bill_detail.json",
            "Charges": "charge_detail.json",
            "DelinquentCharges": "delinquency.json",
            # Financial - General Ledger
            "GeneralLedgerAccounts": "chart_of_accounts.json",
            "GeneralLedgerDetails": "general_ledger.json",
            # Collections
            "CollectionsPlacement": "tenant_debt_collections_status.json",
            # Leads
            "Leads": "guest_cards.json",
            # Other Reports
            "AgedPayablesSummary": "aged_payables_summary.json",
            "AgedReceivableDetail": "aged_receivables_detail.json",
            "DepositRegister": "deposit_register.json",
            "GrossPotentialRent": "gross_potential_rent_enhanced.json",
            "LeaseExpirationDetail": "lease_expiration_detail.json",
            "PurchaseOrder": "purchase_order.json",
            "ReceivablesActivity": "receivables_activity.json",
            "RentRoll": "rent_roll.json",
            "RentRollItemized": "rent_roll_itemized.json",
            "TenantTickler": "tenant_tickler.json",
            "TenantVehicleInfo": "tenant_vehicle_info.json",
            "TrustAccountBalance": "trust_account_balance.json",
            "UnitTurnDetail": "unit_turn_detail.json",
            "UnitVacancyDetail": "unit_vacancy.json",
            "VendorDirectory": "vendor_directory.json",
            "WorkOrder": "work_order.json",
        }

    def fetch_resource(self, resource_name: str, delay: float = 1.0) -> Optional[Dict]:
        """
        Fetch a specific resource from AppFolio API

        Args:
            resource_name: Name of the resource (e.g., 'Tenants', 'Bills')
            delay: Delay in seconds after request (for rate limiting)

        Returns:
            Dictionary containing the API response or None if error
        """
        if resource_name not in self.endpoints:
            print(f"Error: Unknown resource '{resource_name}'")
            print(f"Available resources: {', '.join(self.endpoints.keys())}")
            return None

        endpoint = self.endpoints[resource_name]
        url = f"{self.base_url}{endpoint}"

        try:
            print(f"Fetching {resource_name}...")
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            results_count = len(data.get("results", []))
            print(f"✓ Fetched {resource_name}: {results_count} records")

            # Rate limiting delay
            if delay > 0:
                time.sleep(delay)

            return data

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(
                    f"⚠ Rate limit hit for {resource_name}. Retrying after 3 seconds..."
                )
                time.sleep(3)
                return self.fetch_resource(resource_name, delay)
            else:
                print(
                    f"✗ HTTP Error fetching {resource_name}: {e.response.status_code}"
                )
                print(f"   Response: {e.response.text}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"✗ Error fetching {resource_name}: {str(e)}")
            return None

    def fetch_multiple_resources(
        self, resource_names: List[str], delay: float = 1.0
    ) -> Dict[str, Dict]:
        """
        Fetch multiple resources from AppFolio API

        Args:
            resource_names: List of resource names to fetch
            delay: Delay between requests in seconds

        Returns:
            Dictionary mapping resource names to their data
        """
        results = {}

        for resource_name in resource_names:
            data = self.fetch_resource(resource_name, delay)
            if data:
                results[resource_name] = data

        return results

    def save_to_json(self, data: Dict, filename: str = "appfolio_data.json"):
        """Save fetched data to JSON file"""
        try:
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            print(f"\n✓ Data saved to {filename}")
        except Exception as e:
            print(f"✗ Error saving to file: {str(e)}")


# Quick usage examples
def example_fetch_tenants():
    """Example: Fetch tenants data"""
    api = AppFolioAPI()
    data = api.fetch_resource("Tenants")

    if data and data.get("results"):
        print(f"\nFirst tenant:")
        print(json.dumps(data["results"][0], indent=2))

    return data


def example_fetch_bills():
    """Example: Fetch bills data"""
    api = AppFolioAPI()
    data = api.fetch_resource("Bills")

    if data and data.get("results"):
        print(f"\nFirst bill:")
        print(json.dumps(data["results"][0], indent=2))

    return data


def example_fetch_charges():
    """Example: Fetch charges data"""
    api = AppFolioAPI()
    data = api.fetch_resource("Charges")

    if data and data.get("results"):
        print(f"\nFirst charge:")
        print(json.dumps(data["results"][0], indent=2))

    return data


def example_fetch_owners():
    """Example: Fetch owners data"""
    api = AppFolioAPI()
    data = api.fetch_resource("Owners")

    if data and data.get("results"):
        print(f"\nFirst owner:")
        print(json.dumps(data["results"][0], indent=2))

    return data


def example_fetch_properties():
    """Example: Fetch properties data"""
    api = AppFolioAPI()
    data = api.fetch_resource("Properties")

    if data and data.get("results"):
        print(f"\nFirst property:")
        print(json.dumps(data["results"][0], indent=2))

    return data


def example_fetch_rental_applications():
    """Example: Fetch rental applications"""
    api = AppFolioAPI()
    data = api.fetch_resource("RentalApplications")

    if data and data.get("results"):
        print(f"\nFirst rental application:")
        print(json.dumps(data["results"][0], indent=2))

    return data


def example_fetch_collections():
    """Example: Fetch collections placement data"""
    api = AppFolioAPI()
    data = api.fetch_resource("CollectionsPlacement")

    if data and data.get("results"):
        print(f"\nFirst collections record:")
        print(json.dumps(data["results"][0], indent=2))

    return data


def example_fetch_general_ledger():
    """Example: Fetch general ledger details"""
    api = AppFolioAPI()

    # Fetch both accounts and details
    accounts = api.fetch_resource("GeneralLedgerAccounts")
    details = api.fetch_resource("GeneralLedgerDetails")

    return {"accounts": accounts, "details": details}


def main():
    """Main example demonstrating various API calls"""

    print("=" * 70)
    print("AppFolio API Python Example")
    print("=" * 70)

    try:
        # Initialize API client
        api = AppFolioAPI()
        print(f"\n✓ Connected to: {api.base_url}")

        # Example: Fetch specific resources you asked about
        print("\n--- Fetching Requested Resources ---\n")

        requested_resources = [
            "Bills",
            # "Charges",
            # "CollectionsPlacement",
            # "DelinquentCharges",
            # "GeneralLedgerAccounts",
            # "GeneralLedgerDetails",
            # "Leads",
            # "Owners",
            # "Properties",
            # "PropertyGroups",
            # "RentalApplications",
            # "Tenants",
        ]

        all_data = api.fetch_multiple_resources(requested_resources, delay=1.0)

        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(
            f"\nSuccessfully fetched {len(all_data)}/{len(requested_resources)} resources:\n"
        )

        for resource_name, data in all_data.items():
            results_count = len(data.get("results", []))
            print(f"  • {resource_name:30s} {results_count:5d} records")
            print(data["results"][0])

        # Optionally save to file
        # api.save_to_json(all_data, "appfolio_export.json")

        print("\n" + "=" * 70)

    except ValueError as e:
        print(f"\n✗ Configuration Error: {str(e)}")
        print("\nMake sure your .env file contains:")
        print("  APPFOLIO_CLIENT_ID=your_client_id")
        print("  APPFOLIO_CLIENT_SECRET=your_client_secret")
    except Exception as e:
        print(f"\n✗ Unexpected Error: {str(e)}")


if __name__ == "__main__":
    main()
