from fastapi import APIRouter, Depends, HTTPException
import requests
from ..config import settings
from pydantic import BaseModel

router = APIRouter()

headers = {"Content-Type": "application/json",
           "Authorization": f"Bearer {settings.access_token}"}


class WhatsappMessage(BaseModel):
    message: str


@router.post('/webhook', tags=["whatsapp"])
async def whatsapp_webhook(message: WhatsappMessage):
    body = {
        "messaging_product": "whatsapp",
        "to": "6597714873",
        "type": "template",
        "template": {
            "name": "hello_world",
            "language": {"code": "en_US"}
        }
    }
    r = requests.post(settings.whatsapp_web, headers=headers)
    r
