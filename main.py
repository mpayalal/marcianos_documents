from fastapi import FastAPI, HTTPException
from routes import upload
from google.cloud import storage
from google.auth.exceptions import DefaultCredentialsError
from google.oauth2 import service_account
import os
import json
from dotenv import load_dotenv


app = FastAPI()

app.include_router(upload.router)

@app.get("/verify-gcs")
def verify_gcs_credentials():
    try:
        #prueba
        # credentials_b64 = os.getenv("GCP_CREDENTIALS_JSON")
        # if not credentials_b64:
        #     raise Exception("GCP_CREDENTIALS_JSON not set")

        # decoded = base64.b64decode(credentials_b64)

        # # Guarda el archivo temporalmente
        # with open("/tmp/key.json", "wb") as f:
        #     f.write(decoded)

        # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/tmp/key.json"

        #fin prueba

        # Cargar .env
        load_dotenv()

        # Leer y parsear el JSON desde la variable de entorno
        creds_json = os.getenv("GCP_SA_KEY")

        if not creds_json:
            raise Exception("Falta la variable GCP_SA_KEY")

        creds_dict = json.loads(creds_json)
        print(creds_dict)

        # Crear el cliente con las credenciales
        credentials = service_account.Credentials.from_service_account_info(creds_dict)
        client = storage.Client(credentials=credentials, project=creds_dict["project_id"])

        # client = storage.Client()
        buckets = list(client.list_buckets())
        bucket_names = [bucket.name for bucket in buckets]
        return {"status": "success", "buckets": bucket_names}
    except DefaultCredentialsError as e:
        raise HTTPException(status_code=500, detail=f"Credenciales no encontradas o inválidas: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al acceder a GCS: {e}")
