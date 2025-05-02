from fastapi import FastAPI, HTTPException
from routes import upload
import os
import base64
from google.oauth2 import service_account

app = FastAPI()

app.include_router(upload.router)

@app.get("/check-credentials")
async def check_credentials():
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not creds_path:
        raise HTTPException(status_code=400, detail="GOOGLE_APPLICATION_CREDENTIALS is not set")

    return {"GOOGLE_APPLICATION_CREDENTIALS": creds_path}
