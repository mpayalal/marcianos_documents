from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from google.cloud import storage
from gcstorage_class import GCStorage
from google.oauth2 import service_account
import os
import json

router = APIRouter()

@router.post("/uploadDocument")
async def upload_file_to_user_bucket(
    file: UploadFile = File(...),
    username: str = Form(...)
):
    try:
        # bucket_name = username.lower()
        bucket_name = "mpayalal"

        #prueba
        # Leer JSON desde variable de entorno
        json_str = os.getenv("GCP_CREDENTIALS_JSON")
        if not json_str:
            raise RuntimeError("GCP_CREDENTIALS_JSON not set")

        # Convertir a dict y crear credenciales
        info = json.loads(json_str)
        credentials = service_account.Credentials.from_service_account_info(info)

        # Usar las credenciales explícitas
        gcs = GCStorage(storage.Client(credentials=credentials))

        #fin prueba
        
        # gcs = GCStorage(storage.Client())
        
        if not bucket_name in gcs.list_buckets():
            bucket_gcs = gcs.create_bucket(bucket_name, 'STANDARD')
        else:
            bucket_gcs = gcs.get_bucket(bucket_name)

        content = await file.read()

        gcs.upload_file_from_bytes(bucket_gcs, file.filename, content, file.content_type)

        return {
            "message": f"Archivo '{file.filename}' subido correctamente al bucket '{bucket_name}'",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
