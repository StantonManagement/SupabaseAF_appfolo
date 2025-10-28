import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.services.sync import sync_details
from app.helpers.constants import DETAILS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler("app.log"),  # File output
    ],
)

# Create logger for this module
logger = logging.getLogger(__name__)


app = FastAPI()


class SyncRequest(BaseModel):
    dataset: str


class SyncResponse(BaseModel):
    success: int
    failed: int
    total: int


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/sync_details", response_model=SyncResponse)
def trigger_sync(request: SyncRequest):
    logger.info(f"🚀 API REQUEST RECEIVED - Dataset: '{request.dataset}'")

    # Validate dataset parameter
    if not request.dataset or not isinstance(request.dataset, str):
        logger.warning(
            f"⚠️ API REQUEST FAILED - Invalid dataset parameter: {request.dataset}"
        )
        raise HTTPException(
            status_code=400, detail="Dataset parameter must be a non-empty string"
        )

    # Validate that dataset exists in our supported list
    if request.dataset not in DETAILS:
        logger.warning(
            f"❌ API REQUEST FAILED - Unsupported dataset: '{request.dataset}'"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported dataset '{request.dataset}'. Supported datasets: {', '.join(DETAILS.keys())}",
        )

    try:
        result = sync_details(request.dataset)

        # The sync_details function now returns the success/failed counts
        logger.info(
            f"✅ API RESPONSE SENDING - Dataset: '{request.dataset}', Result: {result}"
        )
        return SyncResponse(**result)

    except ValueError as e:
        logger.error(
            f"💥 API REQUEST FAILED - ValueError for dataset '{request.dataset}': {str(e)}"
        )
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(
            f"🔥 API REQUEST FAILED - RuntimeError for dataset '{request.dataset}': {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(
            f"🚨 API REQUEST FAILED - Unexpected error for dataset '{request.dataset}': {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
