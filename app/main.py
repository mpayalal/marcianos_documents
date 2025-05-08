from fastapi import FastAPI
from routes import upload, list_files, delete,  get_file_url 
from fastapi.middleware.cors import CORSMiddleware
from db.db import engine, Base
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(list_files.router)
app.include_router(delete.router)
app.include_router(get_file_url.router)

@app.on_event("startup")
async def startup_db_client():
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    # Close any open connections or perform cleanup
    logger.info("Shutting down application")

@app.get("/")
async def root():
    return {"message": "Welcome to the Documents API"}
