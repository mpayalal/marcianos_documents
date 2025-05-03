import os
from dotenv import load_dotenv
from google.cloud import storage
from gcstorage_class import GCStorage
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

@router.get("/listDocuments")
async def list_documents_from_user_folder(
    client_id: str = Query(...)
):
    try:
        bucket_name = os.getenv("GCP_BUCKET_NAME")

        load_dotenv()
        creds_path = os.getenv("GCP_SA_KEY")
        gcs = GCStorage(storage.Client.from_service_account_json(creds_path))
        
        blobs = gcs.list_blobs(bucket_name, prefix=f"{client_id}/")
        file_names = [blob.name for blob in blobs]

        return {
            "documents": file_names
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
