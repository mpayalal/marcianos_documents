from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from google.cloud import storage
from gcstorage_class import GCStorage
from google.oauth2 import service_account
import os
import json
from dotenv import load_dotenv

router = APIRouter()

@router.post("/uploadDocument")
async def upload_file_to_user_bucket(
    file: UploadFile = File(...),
    username: str = Form(...)
):
    try:
        bucket_name = username.lower()
        # bucket_name = "mpayalal"

        # Cargar .env
        load_dotenv()

        # Leer y parsear el JSON desde la variable de entorno
        creds_json = os.getenv("GCP_SA_KEY")

        if not creds_json:
            raise Exception("Falta la variable GCP_SA_KEY")

        creds_dict = json.loads(creds_json)

        # Crear el cliente con las credenciales
        credentials = service_account.Credentials.from_service_account_info(creds_dict)
        gcs = GCStorage(storage.Client(credentials=credentials, project=creds_dict["project_id"]))

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
