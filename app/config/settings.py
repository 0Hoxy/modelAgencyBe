"""
애플리케이션 설정 관리
환경 변수를 통한 설정 관리
"""

from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""
    
    # 기본 앱 설정
    APP_NAME: str = "ModelAgencyBe"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 데이터베이스 설정 (ORM 설치 후 활성화)
    # DATABASE_URL: str = ""
    
    # JWT 설정
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS 설정
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """설정 인스턴스 반환 (캐시됨)"""
    return Settings()
