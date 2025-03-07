from fastapi import APIRouter, Depends, HTTPException
import requests
from ..config import settings
from pydantic import BaseModel
import base64


router = APIRouter(prefix="/whatsapp",tags=["whatsapp"])



class WhatsappMessage(BaseModel):
    message: str

class ReplyMessage(BaseModel):
    text:str
    message:str


@router.post('/message', tags=["whatsapp"])
async def whatsapp_webhook(message: WhatsappMessage):

    headers = {"Content-Type": "application/json","Authorization": f"Bearer {settings.access_token}"}

    body = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": "6597714873",
        "type": "text",
        "text": {
            "preview_url": True,
            "body": f"{message.message}"
        }
    }

    r = requests.post(settings.whatsapp_web + "messages", json=body, headers=headers)
    print(r.status_code)
    print(r.text)
    if r.status_code >= 300:
        raise HTTPException(status_code=500, detail=f"{r.text}")
    return {200: {"description": "sucessfully sent message"}}

@router.post('/reply', tags=["whatsapp"])
async def whatsapp_reply_audio_and_text(message : ReplyMessage):
    base64_audio = message.audio
    text = message.text
    bytes_audio = base64.b64decode(base64_audio)
    
    headers = {"Authorization": f"Bearer {settings.access_token}"}
    body = {
        "messaging_product": "whatsapp",
        "file" : "@/src/audio.mp3",
        "type" : "audio/mpeg"
    }
    r = requests.post(settings.whatsapp_web + "media",json=body,headers=headers)
    if r.status_code >= 300:
        raise HTTPException(status_code=404, detail=f"{r.text}")









