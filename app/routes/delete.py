import os
import json
import asyncio
from pydantic import BaseModel
from aio_pika import connect_robust, Message
from fastapi import APIRouter, HTTPException, Form

router = APIRouter()

class DeleteFileRequest(BaseModel):
    client_id: str
    file_name: str

class DeleteFolderRequest(BaseModel):
    client_id: str

rabbitmq_user = os.getenv("RABBITMQ_USER") 
print(rabbitmq_user)
rabbitmq_pass = os.getenv("RABBITMQ_PASSWORD")
print(rabbitmq_pass)
rabbitmq_host = os.getenv("RABBITMQ_HOST")
print(rabbitmq_host)
rabbitmq_port = os.getenv("RABBITMQ_PORT")
print(rabbitmq_port)

async def connect_to_rabbit():
    try:
        connection = await connect_robust(
            host=rabbitmq_host,
            login=rabbitmq_user,
            password=rabbitmq_pass
        )
        print(connection)
        return connection
    except Exception as e:
        raise Exception(f"RabbitMQ connection error: {e}")
    
async def publish_to_rabbitmq(message_body: dict):
    try:
        connection = await connect_to_rabbit()
        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue('delete_files', durable=True)
            message = Message(body=json.dumps(message_body).encode())
            await channel.default_exchange.publish(message, routing_key=queue.name)
    except Exception as e:
        raise Exception(f"RabbitMQ publish error: {e}")

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
        await publish_to_rabbitmq(message)

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
        await publish_to_rabbitmq(message)

        return {"message": f"Los archivos de la carpeta del cliente {client_id} están siendo procesados para eliminación."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
