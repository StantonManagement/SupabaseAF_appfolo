# AppFolio Credentials Checker

A simple tool to validate your AppFolio API credentials and check which resources/tables you have read access to.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure your credentials:**
   
   Make sure your `.env` file contains:
   ```
   APPFOLIO_CLIENT_ID=your_client_id_here
   APPFOLIO_CLIENT_SECRET=your_client_secret_here
   ```

## Usage

Run the checker:
```bash
python check_appfolio_credentials.py
```

## What It Does

1. **Validates Credentials** - Attempts to obtain an OAuth2 access token using your client credentials
2. **Lists Accessible Resources** - Tests common AppFolio API endpoints to see which ones you can read from
3. **Provides Summary** - Shows all resources you have access to, organized by category

## Output

The checker will show:
- ✅ Valid credentials with token information
- ❌ Invalid credentials with error details
- 📋 List of accessible resources organized by category:
  - Property Management (properties, units, leases, tenants, applicants)
  - Financial (invoices, payments, charges, accounts, transactions)
  - Maintenance (work orders, vendors, maintenance requests)
  - Reporting (reports, custom fields)

## Example Output

```
============================================================
  AppFolio Credentials & Access Checker
============================================================

🔐 Checking AppFolio credentials...
   Client ID: 3e1fb254...a08f
   Client Secret: e42ded08...8bc2

✅ Credentials are VALID!
   Access Token: eyJhbGciOiJSUzI1NiIs...
   Token Type: Bearer
   Expires In: 3600 seconds

📋 Checking accessible AppFolio resources...

🔍 Testing Property Management resources:
   ✅ properties - Accessible (READ)
   ✅ units - Accessible (READ)
   ⚠️  leases - Forbidden (no permissions)
   ...

============================================================
📊 SUMMARY
============================================================

✅ You have READ access to the following resources:

  Property Management:
    • properties
    • units
  
  Financial:
    • invoices
    • payments

Total accessible resources: 4

============================================================
```

## Troubleshooting

- **401 Unauthorized**: Your credentials are invalid or expired
- **403 Forbidden**: Your credentials are valid but don't have permission for that resource
- **404 Not Found**: The endpoint may not exist or the API version has changed
- **Network errors**: Check your internet connection and firewall settings
