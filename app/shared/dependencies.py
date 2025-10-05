"""
FastAPI Dependencies
- JWT 인증 미들웨어
- 권한 확인
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials

from app.shared import jwt_handler
from app.domain.accounts.account_repository import AccountRepository
from app.domain.accounts.account_schemas import UserRole


# HTTP Bearer 토큰 스키마
security = HTTPBearer()
account_repository = AccountRepository()


async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> dict:
    """
    현재 로그인한 사용자 정보 반환
    - JWT 토큰 검증
    - 유효하지 않은 토큰이면 401 에러
    """
    token = credentials.credentials
    payload = jwt_handler.verify_token(token, token_type="access")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않거나 만료된 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 사용자 존재 확인
    user = await account_repository.get_by_pid(payload.get("sub"))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "id": user["id"],
        "pid": user["pid"],
        "name": user["name"],
        "role": user["role"],
    }


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """
    관리자 권한 확인
    - ADMIN 역할만 허용
    """
    if current_user["role"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다.",
        )
    return current_user


async def require_admin_or_director(current_user: dict = Depends(get_current_user)) -> dict:
    """
    관리자 또는 디렉터 권한 확인
    - ADMIN 또는 DIRECTOR 역할 허용
    """
    if current_user["role"] not in [UserRole.ADMIN.value, UserRole.DIRECTOR.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 또는 디렉터 권한이 필요합니다.",
        )
    return current_user
