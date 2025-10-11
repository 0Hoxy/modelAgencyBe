from datetime import datetime
from enum import Enum
from uuid import UUID
import re

from pydantic import BaseModel, Field, field_validator, EmailStr


class UserRole(str, Enum):
    """사용자 역할"""
    ADMIN = "ADMIN"
    DIRECTOR = "DIRECTOR"


class Provider(str, Enum):
    """소셜 로그인 제공자"""
    LOCAL = "LOCAL"  # 일반 회원가입
    GOOGLE = "GOOGLE"
    KAKAO = "KAKAO"
    NAVER = "NAVER"


class SignUpRequest(BaseModel):
    """회원가입 요청"""
    name: str = Field(..., min_length=1, max_length=100, description="사용자 이름")
    pid: EmailStr = Field(..., description="이메일 (고유 식별자)")
    password: str = Field(..., min_length=8, max_length=20, description="비밀번호")
    role: UserRole = Field(default=UserRole.DIRECTOR, description="사용자 역할")
    provider: Provider = Field(default=Provider.LOCAL, description="가입 경로")
    provider_id: str | None = Field(None, max_length=255, description="소셜 로그인 ID")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        비밀번호 검증:
        - 8자 이상 20자 이하
        - 영문자, 숫자, 특수문자 각각 1개 이상 포함
        """
        if len(v) < 8 or len(v) > 20:
            raise ValueError('비밀번호는 8자 이상 20자 이하여야 합니다.')
        
        # 영문자 포함 확인
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError('비밀번호는 최소 1개의 영문자를 포함해야 합니다.')
        
        # 숫자 포함 확인
        if not re.search(r'\d', v):
            raise ValueError('비밀번호는 최소 1개의 숫자를 포함해야 합니다.')
        
        # 특수문자 포함 확인
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('비밀번호는 최소 1개의 특수문자를 포함해야 합니다.')
        
        return v

    @field_validator('provider_id')
    @classmethod
    def validate_provider_id(cls, v: str | None, info) -> str | None:
        """소셜 로그인 시 provider_id 필수"""
        provider = info.data.get('provider')
        
        if provider != Provider.LOCAL and not v:
            raise ValueError('소셜 로그인 시 provider_id는 필수입니다.')
        
        return v


class SignUpAdminRequest(SignUpRequest):
    """관리자 회원가입 요청 (role 고정)"""
    role: UserRole = Field(default=UserRole.ADMIN, frozen=True, description="관리자 역할")


class SignUpDirectorRequest(SignUpRequest):
    """감독 회원가입 요청 (role 고정)"""
    role: UserRole = Field(default=UserRole.DIRECTOR, frozen=True, description="감독 역할")


class UserResponse(BaseModel):
    """사용자 정보 응답"""
    id: UUID = Field(..., description="사용자 고유 ID")
    name: str = Field(..., description="사용자 이름")
    pid: str = Field(..., description="이메일")
    role: UserRole = Field(..., description="사용자 역할")
    provider: Provider = Field(..., description="가입 경로")
    created_at: datetime = Field(..., description="가입일시")


class PasswordChangeRequest(BaseModel):
    """비밀번호 변경 요청"""
    pid: EmailStr = Field(..., description="이메일")
    current_password: str = Field(..., description="현재 비밀번호")
    new_password: str = Field(..., min_length=8, max_length=20, description="새 비밀번호")

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """새 비밀번호 검증 (회원가입과 동일)"""
        if len(v) < 8 or len(v) > 20:
            raise ValueError('비밀번호는 8자 이상 20자 이하여야 합니다.')
        
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError('비밀번호는 최소 1개의 영문자를 포함해야 합니다.')
        
        if not re.search(r'\d', v):
            raise ValueError('비밀번호는 최소 1개의 숫자를 포함해야 합니다.')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('비밀번호는 최소 1개의 특수문자를 포함해야 합니다.')
        
        return v


class LoginRequest(BaseModel):
    """로그인 요청"""
    pid: EmailStr = Field(..., description="이메일")
    password: str = Field(..., description="비밀번호")


class LoginResponse(BaseModel):
    """로그인 응답"""
    access_token: str = Field(..., description="JWT 액세스 토큰 (4시간)")
    refresh_token: str = Field(..., description="JWT 리프레시 토큰 (3일)")
    token_type: str = Field(default="bearer", description="토큰 타입")
    user: UserResponse = Field(..., description="사용자 정보")


class RefreshTokenRequest(BaseModel):
    """토큰 갱신 요청"""
    refresh_token: str = Field(..., description="리프레시 토큰")


class RefreshTokenResponse(BaseModel):
    """토큰 갱신 응답"""
    access_token: str = Field(..., description="새로운 JWT 액세스 토큰 (4시간)")
    refresh_token: str = Field(..., description="새로운 JWT 리프레시 토큰 (3일)")
    token_type: str = Field(default="bearer", description="토큰 타입")


class CurrentUserPasswordChangeRequest(BaseModel):
    """현재 로그인한 사용자의 비밀번호 변경 요청"""
    current_password: str = Field(..., description="현재 비밀번호")
    new_password: str = Field(..., min_length=8, max_length=20, description="새 비밀번호")

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        """새 비밀번호 검증 (회원가입과 동일)"""
        if len(v) < 8 or len(v) > 20:
            raise ValueError('비밀번호는 8자 이상 20자 이하여야 합니다.')
        
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError('비밀번호는 최소 1개의 영문자를 포함해야 합니다.')
        
        if not re.search(r'\d', v):
            raise ValueError('비밀번호는 최소 1개의 숫자를 포함해야 합니다.')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('비밀번호는 최소 1개의 특수문자를 포함해야 합니다.')
        
        return v


class AccountResponse(BaseModel):
    """일반 응답"""
    message: str = Field(..., description="응답 메시지")
