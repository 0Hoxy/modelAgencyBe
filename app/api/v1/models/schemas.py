"""
모델 관련 Pydantic 스키마
요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ModelCreate(BaseModel):
    """모델 생성 요청 스키마"""
    name: str = Field(..., min_length=2, max_length=100, description="모델명")
    description: str = Field(..., min_length=10, max_length=500, description="모델 설명")
    category: str = Field(..., description="카테고리")
    price_per_hour: int = Field(..., gt=0, description="시간당 가격")
    specialties: List[str] = Field(default=[], description="전문 분야")
    portfolio_url: Optional[str] = Field(None, description="포트폴리오 URL")


class ModelUpdate(BaseModel):
    """모델 수정 요청 스키마"""
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="모델명")
    description: Optional[str] = Field(None, min_length=10, max_length=500, description="모델 설명")
    category: Optional[str] = Field(None, description="카테고리")
    price_per_hour: Optional[int] = Field(None, gt=0, description="시간당 가격")
    specialties: Optional[List[str]] = Field(None, description="전문 분야")
    portfolio_url: Optional[str] = Field(None, description="포트폴리오 URL")


class ModelResponse(BaseModel):
    """모델 응답 스키마"""
    model_id: str = Field(..., description="모델 ID")
    name: str = Field(..., description="모델명")
    description: str = Field(..., description="모델 설명")
    category: str = Field(..., description="카테고리")
    price_per_hour: int = Field(..., description="시간당 가격")
    specialties: List[str] = Field(..., description="전문 분야")
    portfolio_url: Optional[str] = Field(None, description="포트폴리오 URL")
    is_available: bool = Field(..., description="예약 가능 여부")
    rating: Optional[float] = Field(None, ge=0, le=5, description="평점")
    total_bookings: int = Field(default=0, description="총 예약 수")
    created_at: str = Field(..., description="생성일시")
    updated_at: str = Field(..., description="수정일시")


class ModelListResponse(BaseModel):
    """모델 목록 응답 스키마"""
    models: List[ModelResponse] = Field(..., description="모델 목록")
    total: int = Field(..., description="전체 개수")
    skip: int = Field(..., description="건너뛴 개수")
    limit: int = Field(..., description="가져온 개수")
