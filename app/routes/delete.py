import os
from google.cloud import storage
from gcstorage_class import GCStorage
from fastapi import APIRouter, HTTPException, Form

router = APIRouter()

@router.post("/deleteFolder")
async def delete_folder_from_bucket(
    client_id: str = Form(...)
):
    try:
        creds_path = os.getenv("GCP_SA_KEY")
        bucket_name = os.getenv("GCP_BUCKET_NAME")
        gcs = GCStorage(storage.Client.from_service_account_json(creds_path))
        
        folder = list(gcs.list_blobs(bucket_name, f"{client_id}/"))
        if not folder:
            return {"message": f"No se encontro la carpeta del cliente '{client_id}'"}

        deleted_files = []
        for file in folder:
            deleted_files.append(file.name)
            file.delete()

        return {
            "message": f"Se eliminaron {len(deleted_files)} archivos del cliente {client_id}.",
            "files": deleted_files
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
