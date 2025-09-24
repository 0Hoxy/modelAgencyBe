"""
애플리케이션 설정 관리
"""

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # 앱 기본 설정
    APP_NAME: str = "ModelAgencyBe"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 데이터베이스 설정
    DATABASE_URL: str = "postgresql+asyncpg://modelagency_user:password@localhost:5432/modelagency_dev"
    
    # JWT 설정
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS 설정
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    
    # 파일 업로드 설정
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB 파일 크기 제한
    UPLOAD_DIR: str = "uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 전역 설정 인스턴스
settings = Settings()
