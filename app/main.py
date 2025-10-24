from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.services.sync import sync_details
from app.helpers.constants import DETAILS


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
    # Validate dataset parameter
    if not request.dataset or not isinstance(request.dataset, str):
        raise HTTPException(
            status_code=400, detail="Dataset parameter must be a non-empty string"
        )

    # Validate that dataset exists in our supported list
    if request.dataset not in DETAILS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported dataset '{request.dataset}'. Supported datasets: {', '.join(DETAILS.keys())}",
        )

    try:
        result = sync_details(request.dataset)

        # The sync_details function now returns the success/failed counts
        return SyncResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
