"""
애플리케이션 설정 관리
"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 앱 기본 설정
    APP_NAME: str
    DEBUG: bool
    HOST: str
    PORT: int

    # 데이터베이스 설정
    DATABASE_URL: str

    # JWT 설정
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # CORS 설정
    ALLOWED_ORIGINS: str

    # 파일 업로드 설정
    MAX_FILE_SIZE: int
    UPLOAD_DIR: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 전역 설정 인스턴스
settings = Settings()
