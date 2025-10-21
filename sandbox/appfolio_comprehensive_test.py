import os
import requests
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AppFolio API credentials
CLIENT_ID = os.getenv("APPFOLIO_CLIENT_ID")
CLIENT_SECRET = os.getenv("APPFOLIO_CLIENT_SECRET")

def test_all_possible_endpoints():
    """
    Test multiple possible AppFolio API endpoint patterns
    """

    # Possible OAuth endpoint patterns
    auth_endpoints = [
        "https://stantonmgmt.appfolio.com/oauth/token",
        "https://api.appfolio.com/oauth2/token",
        "https://api.appfolio.com/v2/stantonmgmt/oauth/token",
        "https://appfolio.com/oauth/token",
        "https://api.appfolio.com/v1/oauth/token"
    ]

    # Possible API endpoints for charges
    api_endpoints = [
        ("https://stantonmgmt.appfolio.com", "/api/v1/charges"),
        ("https://api.appfolio.com", "/v2/stantonmgmt/charges"),
        ("https://api.appfolio.com", "/v1/stantonmgmt/charges"),
        ("https://stantonmgmt.appfolio.com", "/v2/charges"),
    ]

    # Test data
    auth_data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    print(f"Client ID present: {bool(CLIENT_ID)}")
    print(f"Client Secret present: {bool(CLIENT_SECRET)}")
    print(f"Client ID starts with: {CLIENT_ID[:10] if CLIENT_ID else 'None'}...")
    print("\n" + "="*60)
    print("TESTING OAUTH ENDPOINTS")
    print("="*60)

    # Test each OAuth endpoint
    for i, auth_url in enumerate(auth_endpoints, 1):
        print(f"\n{i}. Testing: {auth_url}")
        try:
            response = requests.post(auth_url, data=auth_data, headers=headers, timeout=10)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get("access_token")
                print(f"   ✓ SUCCESS! Got token: {access_token[:20] if access_token else 'None'}...")

                # If successful, test API endpoints with this token
                print(f"\n   Testing API endpoints with token...")

                for j, (base_url, endpoint) in enumerate(api_endpoints, 1):
                    print(f"   {j}. {base_url}{endpoint}")

                    api_headers = {
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    }

                    params = {"limit": 1}

                    try:
                        api_response = requests.get(
                            f"{base_url}{endpoint}",
                            headers=api_headers,
                            params=params,
                            timeout=10
                        )
                        print(f"      Status: {api_response.status_code}")

                        if api_response.status_code == 200:
                            print("      ✓ SUCCESS! Got charges data")
                            charges = api_response.json()
                            print(f"      Data preview: {str(charges)[:100]}...")
                            return True  # Success! We can exit
                        else:
                            print(f"      Response: {api_response.text[:100]}...")
                    except Exception as e:
                        print(f"      Error: {str(e)}")

            elif response.status_code == 401:
                print("   ✗ Authentication failed (401) - Invalid credentials")
                print(f"   Response: {response.text[:100]}...")
            elif response.status_code == 404:
                print("   ✗ Not found (404) - Invalid endpoint")
            elif response.status_code == 405:
                print("   ✗ Method not allowed (405) - Wrong HTTP method")
            else:
                print(f"   ✗ Error: {response.status_code}")
                print(f"   Response: {response.text[:100]}...")

        except requests.exceptions.Timeout:
            print("   ✗ Timeout - Request took too long")
        except requests.exceptions.ConnectionError:
            print("   ✗ Connection error - Could not reach server")
        except Exception as e:
            print(f"   ✗ Error: {str(e)}")

    # Try basic auth as alternative
    print(f"\n" + "="*60)
    print("TRYING BASIC AUTHENTICATION")
    print("="*60)

    # Basic auth approach
    basic_auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    basic_auth_bytes = basic_auth_string.encode('ascii')
    basic_auth_b64 = base64.b64encode(basic_auth_bytes).decode('ascii')

    for j, (base_url, endpoint) in enumerate(api_endpoints, 1):
        print(f"\n{j}. Testing Basic Auth: {base_url}{endpoint}")

        basic_headers = {
            "Authorization": f"Basic {basic_auth_b64}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        params = {"limit": 1}

        try:
            response = requests.get(
                f"{base_url}{endpoint}",
                headers=basic_headers,
                params=params,
                timeout=10
            )
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                print("   ✓ SUCCESS! Basic auth worked")
                charges = response.json()
                print(f"   Data preview: {str(charges)[:100]}...")
                return True
            else:
                print(f"   Response: {response.text[:100]}...")

        except Exception as e:
            print(f"   Error: {str(e)}")

    print(f"\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("All endpoint combinations tested. No successful authentication found.")
    print("Possible issues:")
    print("1. Invalid client credentials (CLIENT_ID or CLIENT_SECRET)")
    print("2. AppFolio account does not have API access enabled")
    print("3. Different subdomain required")
    print("4. Additional API permissions needed")
    print("5. AppFolio API structure has changed")

    return False

if __name__ == "__main__":
    test_all_possible_endpoints()