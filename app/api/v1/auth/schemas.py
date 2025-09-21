"""
인증 관련 Pydantic 스키마
요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class LoginRequest(BaseModel):
    """로그인 요청 스키마"""
    username: str = Field(..., min_length=3, max_length=50, description="사용자명")
    password: str = Field(..., min_length=6, description="비밀번호")


class RegisterRequest(BaseModel):
    """회원가입 요청 스키마"""
    username: str = Field(..., min_length=3, max_length=50, description="사용자명")
    email: EmailStr = Field(..., description="이메일")
    password: str = Field(..., min_length=6, description="비밀번호")
    full_name: str = Field(..., min_length=2, max_length=100, description="실명")
    phone: Optional[str] = Field(None, description="전화번호")


class TokenResponse(BaseModel):
    """토큰 응답 스키마"""
    access_token: str = Field(..., description="액세스 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")
    expires_in: int = Field(..., description="만료 시간(초)")


class UserResponse(BaseModel):
    """사용자 정보 응답 스키마"""
    user_id: str = Field(..., description="사용자 ID")
    username: str = Field(..., description="사용자명")
    email: str = Field(..., description="이메일")
    full_name: str = Field(..., description="실명")
    phone: Optional[str] = Field(None, description="전화번호")
    is_active: bool = Field(default=True, description="활성 상태")
    created_at: str = Field(..., description="생성일시")
