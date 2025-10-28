import logging
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

# Create logger for this module
logger = logging.getLogger(__name__)

credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
encoded_credentials = base64.b64encode(credentials.encode()).decode()
headers = {
    "Authorization": f"Basic {encoded_credentials}",
    "Content-Type": "application/json",
}


def get_appfolio_details(dataset: str):
    logger.info("🌐 FETCHING DATA FROM APPFOLIO API")

    # Validate required environment variables
    if not all([CLIENT_ID, CLIENT_SECRET, V1_BASE_URL, V2_BASE_URL]):
        logger.error(
            "🔑 Missing required AppFolio API credentials in environment variables"
        )
        raise ValueError(
            "Missing required AppFolio API credentials in environment variables"
        )

    # Validate dataset parameter
    if not dataset or not isinstance(dataset, str):
        logger.error(f"❌ Invalid dataset parameter: {dataset}")
        raise ValueError("Dataset parameter must be a non-empty string")

    try:
        if dataset in v1_dataset:
            response = requests.get(
                f"{V1_BASE_URL}/{dataset}", headers=headers, timeout=30
            )
        else:
            response = requests.post(
                f"{V2_BASE_URL}/{dataset}", headers=headers, timeout=30
            )

        # Check for HTTP errors
        response.raise_for_status()

        # Validate response content
        if (
            response.headers.get("content-type", "")
            .lower()
            .startswith("application/json")
        ):
            data = response.json()

            if "results" not in data:
                logger.error(
                    f"📋 Invalid API response: missing 'results' field for dataset '{dataset}'"
                )
                raise ValueError(
                    f"Invalid API response: missing 'results' field for dataset '{dataset}'"
                )

            results = data["results"]
            if not isinstance(results, list):
                logger.error(
                    f"📋 Invalid API response: 'results' field must be a list for dataset '{dataset}'"
                )
                raise ValueError(
                    f"Invalid API response: 'results' field must be a list for dataset '{dataset}'"
                )

            logger.info(f"✅ SUCCESSFULLY FETCHED {len(results)} RECORDS FROM APPFOLIO")
            return results
        else:
            logger.error(
                f"📄 Invalid content-type in API response: {response.headers.get('content-type')}"
            )
            raise ValueError(
                f"Invalid content-type in API response: {response.headers.get('content-type')}"
            )

    except requests.exceptions.Timeout:
        logger.error(f"⏰ AppFolio API request timed out for dataset '{dataset}'")
        raise RuntimeError(f"AppFolio API request timed out for dataset '{dataset}'")
    except requests.exceptions.ConnectionError:
        logger.error(f"🔌 Failed to connect to AppFolio API for dataset '{dataset}'")
        raise RuntimeError(f"Failed to connect to AppFolio API for dataset '{dataset}'")
    except requests.exceptions.HTTPError:
        logger.error(
            f"🚨 AppFolio API HTTP error for dataset '{dataset}': {response.status_code} - {response.text}"
        )
        raise RuntimeError(
            f"AppFolio API HTTP error for dataset '{dataset}': {response.status_code} - {response.text}"
        )
    except requests.exceptions.RequestException as e:
        logger.error(
            f"💥 AppFolio API request failed for dataset '{dataset}': {str(e)}"
        )
        raise RuntimeError(
            f"AppFolio API request failed for dataset '{dataset}': {str(e)}"
        )
    except ValueError as e:
        logger.error(
            f"⚠️ AppFolio API validation error for dataset '{dataset}': {str(e)}"
        )
        raise RuntimeError(
            f"AppFolio API validation error for dataset '{dataset}': {str(e)}"
        )
