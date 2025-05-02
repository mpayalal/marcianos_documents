from fastapi import FastAPI
from routes import upload
import os

app = FastAPI()

app.include_router(upload.router)

@app.get("/check-credentials")
async def check_credentials():
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    return {"GOOGLE_APPLICATION_CREDENTIALS": creds_path}
