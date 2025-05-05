import os
from google.cloud import storage
from gcstorage_class import GCStorage
from fastapi import APIRouter, HTTPException, Form

router = APIRouter()

@router.delete("/v1/documents/folder/{client_id}")
async def delete_folder_from_bucket(client_id: str):
    try:
        creds_path = os.getenv("GCP_SA_KEY")
        bucket_name = os.getenv("GCP_BUCKET_NAME")
        gcs = GCStorage(storage.Client.from_service_account_json(creds_path))
        
        prefix_folder = f"{client_id}/"
        folder = list(gcs.list_blobs(bucket_name, prefix_folder))
        if not folder:
            return {"message": f"No se encontro la carpeta del cliente '{client_id}'"}

        deleted_files = []
        for file in folder:
            clean_name = file.name[len(prefix_folder):] if file.name.startswith(prefix_folder) else file.name
            deleted_files.append(clean_name)
            file.delete()

        # Eliminar posible "objeto-carpeta"
        bucket = gcs.get_bucket(bucket_name)
        placeholder_blob = bucket.blob(f"{client_id}/")
        if placeholder_blob.exists():
            placeholder_blob.delete()

        return {
            "message": f"Se eliminaron {len(deleted_files)} archivos del cliente {client_id}.",
            "files": deleted_files
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
