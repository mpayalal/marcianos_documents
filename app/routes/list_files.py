import os
import datetime
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
        load_dotenv()
        creds_path = os.getenv("GCP_SA_KEY")
        gcs = GCStorage(storage.Client.from_service_account_json(creds_path))

        bucket_name = os.getenv("GCP_BUCKET_NAME")
        documents = {}    

        for blob in gcs.list_blobs(bucket_name, f"{client_id}/"):
            # Generara URL prefirmada para ver el archivo
            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(minutes=15),
                method="GET",
            )

            # Obtener nombre del archivo y ponerlo como llave
            documents[os.path.basename(blob.name)] = url

        return {
            "documents": documents
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
