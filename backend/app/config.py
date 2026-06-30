from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    secret_key: str = "changeme"
    access_token_expire_minutes: int = 43200  # 30 Tage, App-Login soll selten noetig sein

    admin_username: str = "admin"
    admin_password: str = "changeme-admin-password"

    data_path: str = "/app/data"
    images_path: str = "/app/images"
    api_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:8084"

    # KI laeuft on-device in der Android-App, siehe ANDROID_INTEGRATION.md.
    # Diese Variablen sind fuer einen moeglichen spaeteren Cloud-Provider vorbereitet.
    ai_provider: str = "none"
    ai_api_key: Optional[str] = None
    ai_model: str = "on-device"

    class Config:
        env_file = ".env"


settings = Settings()
