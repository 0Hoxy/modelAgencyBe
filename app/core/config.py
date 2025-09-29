from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Final

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        frozen=True,
        case_sensitive=False,
        env_file='.env',
        env_file_encoding='utf-8')

    # 데이터베이스 설정
    DATABASE_URL: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # 애플리케이션 설정
    APP_NAME: str
    DEBUG: bool
    HOST: str
    PORT: int

    # JWT 설정
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # CORS 설정
    ALLOWED_ORIGINS: str

    # 파일 업로드 설정
    MAX_FILE_SIZE: int
    UPLOAD_DIR: str

settings: Final[Settings] = Settings()