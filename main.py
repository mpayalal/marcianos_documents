from fastapi import FastAPI
from routes import upload
import os
import base64
from google.oauth2 import service_account

app = FastAPI()

app.include_router(upload.router)

@app.get("/check-credentials")
async def check_credentials():
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    # Decodificar las credenciales desde base64
    decoded_credentials = base64.b64decode(creds_path)

    # Cargar las credenciales en Google Cloud
    credentials = service_account.Credentials.from_service_account_info(decoded_credentials)

    return {"GOOGLE_APPLICATION_CREDENTIALS": credentials}
