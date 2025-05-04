from fastapi import FastAPI, HTTPException
from routes import upload, list_files, delete
from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError
import os
from dotenv import load_dotenv


app = FastAPI()

app.include_router(upload.router)
app.include_router(list_files.router)
app.include_router(delete.router)
