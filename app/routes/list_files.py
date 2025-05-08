import os
import datetime
from dotenv import load_dotenv
from google.cloud import storage
from gcstorage_class import GCStorage
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session

from dependencies.auth import get_current_user
from models.User import User
from models.File import File
from db.db import get_session

router = APIRouter()

@router.get("/v1/documents/folder")
async def list_documents_from_user_folder(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    try:
        load_dotenv()
        creds_path = os.getenv("GCP_SA_KEY")
        gcs = GCStorage(storage.Client.from_service_account_json(creds_path))

        bucket_name = os.getenv("GCP_BUCKET_NAME")
        documents = {}    
        
        # Use the user's documentNumber as folder name
        folder_name = user.documentNumber

        documentsDb = File.get_all_files_by_user_id(session, user.id)
        if not documentsDb:
            return {"documents": []}
        
        return { "documents": documentsDb }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/v1/documents/folder/{client_id}")
async def list_documents_user(client_id: str):
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
            documents[os.path.basename(blob.name)] = {
                "url": url,
                "firmado": blob.metadata.get("firmado")
            }
        return documents

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))