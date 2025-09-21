"""
인증 관련 API 라우터
로그인, 회원가입, 토큰 갱신 등
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.core.dependencies import get_current_user
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

# 인증 라우터 생성
auth_router = APIRouter()


@auth_router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """
    사용자 로그인
    """
    # TODO: 실제 로그인 로직 구현
    # 1. 사용자 인증
    # 2. JWT 토큰 생성
    # 3. 토큰 반환
    
    return TokenResponse(
        access_token="temp_access_token",
        token_type="bearer",
        expires_in=1800
    )


@auth_router.post("/register", response_model=TokenResponse)
async def register(register_data: RegisterRequest):
    """
    사용자 회원가입
    """
    # TODO: 실제 회원가입 로직 구현
    # 1. 사용자 정보 검증
    # 2. 비밀번호 해싱
    # 3. 사용자 생성
    # 4. JWT 토큰 생성
    
    return TokenResponse(
        access_token="temp_access_token",
        token_type="bearer",
        expires_in=1800
    )


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """
    토큰 갱신
    """
    # TODO: 토큰 갱신 로직 구현
    
    return TokenResponse(
        access_token="new_access_token",
        token_type="bearer",
        expires_in=1800
    )


@auth_router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    사용자 로그아웃
    """
    # TODO: 로그아웃 로직 구현 (토큰 무효화 등)
    
    return {"message": "로그아웃되었습니다"}


@auth_router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    현재 사용자 정보 조회
    """
    return current_user
