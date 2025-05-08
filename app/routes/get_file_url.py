import os
import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from dependencies.auth import get_current_user
from sqlmodel import Session
from google.cloud import storage
from gcstorage_class import GCStorage
from models.User import User
from db.db import get_session
from models.File import File as FileModel

router = APIRouter()

@router.get("/v1/documents/getSignedUrl")
async def get_signed_url(
    file_name: str = Query(..., description="Name of the file to generate signed URL for"),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    try:
        # Verify the file exists and belongs to the user
        file = session.query(FileModel).filter(
            FileModel.user_id == user.id,
            FileModel.file_name == file_name
        ).first()
        
        
        if not file:
            print(f"File name: {file_name}")
            print(f"User ID: {user.id}")
            raise HTTPException(status_code=404, detail="File not found or you don't have permission to access it")
        
        # Get the file path (which includes user's folder)
        file_path = file.file_path
        bucket_name = os.getenv("GCP_BUCKET_NAME")
        
        # Initialize GCS client
        creds_path = os.getenv("GCP_SA_KEY")
        gcs = GCStorage(storage.Client.from_service_account_json(creds_path))
        bucket = gcs.get_bucket(bucket_name)
        blob = bucket.blob(file_path)
        
        # Generate signed URL with 1 hour expiration
        expiration = datetime.timedelta(hours=1)
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=expiration,
            method="GET",
        )

        return {
            "file_name": file_name,
            "signed_url": signed_url,
            "authenticated": file.authenticated,
            "type": file.type,
            "expires_in": str(expiration)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))