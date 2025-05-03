from fastapi import FastAPI, HTTPException
from routes import upload
from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError
from google.oauth2 import service_account
import os
import json

app = FastAPI()

app.include_router(upload.router)

@app.get("/verify-gcs")
def verify_gcs_credentials():
    try:
        #prueba
        # Leer JSON desde variable de entorno
        json_str = os.getenv("GCP_CREDENTIALS_JSON")
        if not json_str:
            raise RuntimeError("GCP_CREDENTIALS_JSON not set")

        # Convertir a dict y crear credenciales
        info = json.loads(json_str)
        credentials = service_account.Credentials.from_service_account_info(info)

        #fin prueba

        client = storage.Client(credentials=credentials)
        buckets = list(client.list_buckets())
        bucket_names = [bucket.name for bucket in buckets]
        return {"status": "success", "buckets": bucket_names}
    except DefaultCredentialsError as e:
        raise HTTPException(status_code=500, detail=f"Credenciales no encontradas o inválidas: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al acceder a GCS: {e}")
