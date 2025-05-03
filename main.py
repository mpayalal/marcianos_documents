from fastapi import FastAPI, HTTPException
from routes import upload
from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError
from google.oauth2 import service_account
import os
import json
from dotenv import load_dotenv


app = FastAPI()

app.include_router(upload.router)

@app.get("/verify-gcs")
def verify_gcs_credentials():
    try:
        # Tomar variable de entorno 
        load_dotenv()
        creds_path = os.getenv("GCP_SA_KEY")
        print(creds_path)

        client = storage.Client.from_service_account_json(creds_path)

        # client = storage.Client()
        buckets = list(client.list_buckets())
        bucket_names = [bucket.name for bucket in buckets]
        return {"status": "success", "buckets": bucket_names}
    except DefaultCredentialsError as e:
        raise HTTPException(status_code=500, detail=f"Credenciales no encontradas o inválidas: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al acceder a GCS: {e}")
