from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    whatsapp_web: str
    access_token: str
    openai_api_key: str
    langsmith_tracing: bool
    langsmith_api_key: str
    groq_api_key: str
    tavily_api_key: str
    jigsawstack_api_key: str
    telegram_bot_token: str
settings = Settings()
