import os
import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from dependencies.auth import get_current_user
from sqlmodel import Session
from google.cloud import storage
from gcstorage_class import GCStorage
from models.User import User
from db.db import get_session
from models.File import File as FileModel

router = APIRouter()

@router.post("/v1/documents/uploadDocument")
async def upload_file_to_user_folder(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    try:
        # Use documentNumber as folder name for organization
        folder_name = user.documentNumber
        bucket_name = os.getenv("GCP_BUCKET_NAME")

        creds_path = os.getenv("GCP_SA_KEY")
        gcs = GCStorage(storage.Client.from_service_account_json(creds_path))
        
        if not bucket_name in gcs.list_buckets():
            bucket_gcs = gcs.create_bucket(bucket_name, 'STANDARD')
        else:
            bucket_gcs = gcs.get_bucket(bucket_name)

        file_name = f"{folder_name}/{file.filename}"
        metadata = {"firmado": "false"}
        gcs.upload_file_from_stream(bucket_gcs, file_name, file.file, file.content_type, metadata)
        
        existing_file = session.query(FileModel).filter(
            FileModel.user_id == user.id,
            FileModel.file_name == file.filename
        ).first()
        
        print(f"Existing file: {existing_file}")
        
        if existing_file:
            # Update existing record
            existing_file.type = file.content_type
            existing_file.file_path = file_name
            existing_file.updated_at = datetime.datetime.utcnow()
            session.commit()
            return {
                "message": f"Archivo '{file.filename}' actualizado correctamente en la carpeta '{folder_name}'",
                "file_id": existing_file.id
            }
        else:
            # Create new database record
            db_file = FileModel.create_new(
                user_id=user.id, 
                file_name=file.filename,
                file_type=file.content_type
            )
            db_file.file_path = file_name
            session.add(db_file)
            session.commit()
            
            return {
                "message": f"Archivo '{file.filename}' subido correctamente a la carpeta '{folder_name}'",
                "file_id": db_file.id
            }

    except Exception as e:
        print(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
