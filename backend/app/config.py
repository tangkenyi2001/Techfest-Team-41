from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    whatsapp_web: str
    access_token: str

settings = Settings()
