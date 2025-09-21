"""
의존성 주입 모듈
FastAPI의 Depends를 활용한 의존성 관리
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config.settings import Settings, get_settings

# HTTP Bearer 토큰 스키마
security = HTTPBearer()


def get_current_settings() -> Settings:
    """설정 의존성"""
    return get_settings()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    현재 사용자 의존성 (JWT 토큰 검증)
    실제 구현 시 JWT 토큰을 검증하고 사용자 정보를 반환
    """
    # TODO: JWT 토큰 검증 로직 구현
    # 현재는 임시로 토큰을 그대로 반환
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 임시 사용자 정보 반환
    return {
        "user_id": "temp_user_id",
        "username": "temp_user",
        "token": credentials.credentials
    }


def get_admin_user(current_user: dict = Depends(get_current_user)):
    """
    관리자 사용자 의존성
    관리자 권한이 있는 사용자만 접근 가능
    """
    # TODO: 실제 권한 검증 로직 구현
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다"
        )
    return current_user
