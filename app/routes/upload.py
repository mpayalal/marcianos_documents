import os
from dotenv import load_dotenv
from google.cloud import storage
from gcstorage_class import GCStorage
from fastapi import APIRouter, UploadFile, File, HTTPException, Form

router = APIRouter()

@router.post("/v1/documents/uploadDocument")
async def upload_file_to_user_folder(
    file: UploadFile = File(...),
    client_id: str = Form(...)
):
    try:
        bucket_name = 'lotso_bucket'

        load_dotenv()
        creds_path = os.getenv("GCP_SA_KEY")
        gcs = GCStorage(storage.Client.from_service_account_json(creds_path))
        
        if not bucket_name in gcs.list_buckets():
            bucket_gcs = gcs.create_bucket(bucket_name, 'STANDARD')
        else:
            bucket_gcs = gcs.get_bucket(bucket_name)

        # content = await file.read()
        file_name = f"{client_id}/{file.filename}"
        metadata = {"firmado": "false"}
        gcs.upload_file_from_stream(bucket_gcs, file_name,  file.file, file.content_type, metadata)

        return {
            "message": f"Archivo '{file.filename}' subido correctamente a la carpeta '{client_id}'",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
