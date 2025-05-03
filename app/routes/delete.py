from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel
import json
import pika  # RabbitMQ client
from google.cloud import storage

router = APIRouter()

class DeleteFileRequest(BaseModel):
    client_id: str
    file_name: str

class DeleteFolderRequest(BaseModel):
    client_id: str

def publish_to_rabbitmq(message: dict):
    # Conectar a RabbitMQ y publicar el mensaje
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='my-rabbitmq.rabbitmq-ns.svc.cluster.local', 
        port=5672
    ))
    channel = connection.channel()

    # Cola de eliminación
    channel.queue_declare(queue='delete_files', durable=True)

    # Mandamos mensaje
    channel.basic_publish(
        exchange='',
        routing_key='delete_files',
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,
        )
    )

    connection.close()

@router.post("/deleteFile")
async def delete_file_from_bucket(
    client_id: str = Form(...),
    file_name: str = Form(...)
):
    try:
        # Mensaje para RabbitMQ
        message = {
            "operation": "delete_file",
            "client_id": client_id,
            "file_name": file_name
        }

        # Mandamos mensaje
        publish_to_rabbitmq(message)

        return {"message": f"El archivo '{file_name}' del cliente {client_id} está siendo procesado para eliminación."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/deleteFolder")
async def delete_folder_from_bucket(
    client_id: str = Form(...)
):
    try:
        # Mensaje para RabbitMQ
        message = {
            "operation": "delete_folder",
            "client_id": client_id
        }

        # Mandamos mensaje
        publish_to_rabbitmq(message)

        return {"message": f"Los archivos de la carpeta del cliente {client_id} están siendo procesados para eliminación."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
