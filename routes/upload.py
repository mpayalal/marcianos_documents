from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from google.cloud import storage
from gcstorage_class import GCStorage

router = APIRouter()

@router.post("/uploadDocument")
async def upload_file_to_user_bucket(
    file: UploadFile = File(...),
    username: str = Form(...)
):
    try:
        # bucket_name = username.lower()
        bucket_name = "mpayalal"
        gcs = GCStorage(storage.Client())
        
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
