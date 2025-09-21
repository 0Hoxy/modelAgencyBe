"""
기본 스키마 클래스들
공통으로 사용되는 기본 스키마 정의
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BaseResponse(BaseModel):
    """기본 응답 스키마"""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = datetime.now()


class PaginationParams(BaseModel):
    """페이징 파라미터 스키마"""
    skip: int = 0
    limit: int = 10


class PaginatedResponse(BaseModel):
    """페이징된 응답 스키마"""
    total: int
    skip: int
    limit: int
    has_next: bool
    has_prev: bool


class ErrorResponse(BaseModel):
    """에러 응답 스키마"""
    success: bool = False
    error_code: str
    error_message: str
    timestamp: datetime = datetime.now()
