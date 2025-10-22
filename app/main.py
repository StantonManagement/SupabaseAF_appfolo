from fastapi import FastAPI
from pydantic import BaseModel

from app.services.sync import sync_details


app = FastAPI()


class SyncRequest(BaseModel):
    dataset: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/sync_details")
def trigger_sync(request: SyncRequest):
    data = sync_details(request.dataset)
    return {"status": data}
