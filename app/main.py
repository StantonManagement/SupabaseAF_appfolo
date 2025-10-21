from fastapi import FastAPI

from app.services.sync import sync_bill_details

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/bill_details")
def trigger_bill_detail_sync():
    # sync_bill_details()
    return {"status": "bill_detail updated"}
