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
        "recipient_type": "individual",
        "to": "6597714873",
        "type": "text",
        "text": {
                "preview_url" : True,
                "body": f"{message.message}"
        }
    }
    r = requests.post(settings.whatsapp_web, json=body, headers=headers)
    print(r.status_code)
    print(r.text)
    if r.status_code >= 300:
        raise HTTPException(status_code=500, detail=f"{r.text}")
    return {200 : {"description" : "sucessfully sent message"}}
