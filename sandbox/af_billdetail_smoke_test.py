#!/usr/bin/env python3
import json
import os
from typing import Optional

import requests

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None


def resolve_supabase_url() -> Optional[str]:
    """Return the Supabase REST URL using env vars or DATABASE_URL fallback."""
    url = os.getenv("SUPABASE_URL")
    if url:
        return url.rstrip("/")

    database_url = os.getenv("DATABASE_URL", "").strip("'\"")
    if "@db." in database_url and ".supabase.co" in database_url:
        try:
            project_section = database_url.split("@db.", 1)[1]
            project_id = project_section.split(".supabase.co", 1)[0]
            return f"https://{project_id}.supabase.co"
        except (IndexError, ValueError):
            return None
    return None


def resolve_api_key() -> Optional[str]:
    """Return the service role or anon key for Supabase REST."""
    return os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")


def main() -> int:
    if load_dotenv:
        load_dotenv()

    base_url = resolve_supabase_url()
    if not base_url:
        print(
            "Supabase URL not found. Set SUPABASE_URL or provide a compatible DATABASE_URL."
        )
        return 1

    api_key = resolve_api_key()
    if not api_key:
        print(
            "Supabase API key not found. Set SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY."
        )
        return 1

    endpoint = f"{base_url}/rest/v1/AF_BillDetail"
    params = {"select": "*", "limit": "1"}
    headers = {
        "Accept": "application/json",
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Prefer": "return=representation",
    }

    print("=== AF_BillDetail smoke test ===")
    print(f"Endpoint: {endpoint}")
    print("Fetching a single row...\n")

    try:
        response = requests.get(endpoint, params=params, headers=headers, timeout=15)
    except Exception as exc:  # pragma: no cover
        print(f"Request failed: {exc}")
        return 1

    if response.status_code != 200:
        print(f"Request returned status {response.status_code}")
        detail = response.text.strip()
        if detail:
            print(f"Response body: {detail[:500]}")
        return 1

    rows = response.json()
    if not rows:
        print("Query succeeded but the table returned no rows.")
        return 0

    sample = rows[0]
    print("Query succeeded. First row:")
    print(json.dumps(sample, indent=2, default=str))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
