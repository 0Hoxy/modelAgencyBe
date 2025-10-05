"""
SMTP 관련 스키마
- 임시 비밀번호 발송 요청/응답
"""
from pydantic import BaseModel, EmailStr, Field


class TempPasswordRequest(BaseModel):
    """임시 비밀번호 발송 요청"""
    pid: EmailStr = Field(..., description="사용자 이메일 (계정 식별자)")


class TempPasswordResponse(BaseModel):
    """임시 비밀번호 발송 응답"""
    message: str = Field(..., description="처리 결과 메시지")
    email: str = Field(..., description="임시 비밀번호가 발송된 이메일 주소")
