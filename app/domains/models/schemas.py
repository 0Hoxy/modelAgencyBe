"""
모델(인물) 관련 Pydantic 스키마
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# Base 스키마
class BaseModelSchema(BaseModel):
    """모델 기본 스키마"""
    name: str = Field(..., min_length=2, max_length=100, description="모델 이름")
    email: EmailStr = Field(..., description="이메일")
    phone: Optional[str] = Field(None, max_length=20, description="전화번호")
    
    # 기본 정보
    age: Optional[int] = Field(None, ge=0, le=100, description="나이")
    height: Optional[int] = Field(None, ge=100, le=250, description="키(cm)")
    weight: Optional[int] = Field(None, ge=30, le=200, description="몸무게(kg)")
    gender: Optional[str] = Field(None, max_length=10, description="성별")
    
    # 상세 정보
    bio: Optional[str] = Field(None, max_length=1000, description="자기소개")
    experience: Optional[str] = Field(None, max_length=2000, description="경력")
    specialties: Optional[List[str]] = Field(None, description="전문 분야")


class ModelCreate(BaseModelSchema):
    """모델 생성 스키마"""
    pass


class ModelUpdate(BaseModel):
    """모델 수정 스키마"""
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="모델 이름")
    phone: Optional[str] = Field(None, max_length=20, description="전화번호")
    age: Optional[int] = Field(None, ge=0, le=100, description="나이")
    height: Optional[int] = Field(None, ge=100, le=250, description="키(cm)")
    weight: Optional[int] = Field(None, ge=30, le=200, description="몸무게(kg)")
    gender: Optional[str] = Field(None, max_length=10, description="성별")
    bio: Optional[str] = Field(None, max_length=1000, description="자기소개")
    experience: Optional[str] = Field(None, max_length=2000, description="경력")
    specialties: Optional[List[str]] = Field(None, description="전문 분야")
    is_active: Optional[bool] = Field(None, description="활성 상태")


class ModelResponse(BaseModelSchema):
    """모델 응답 스키마"""
    id: str = Field(..., description="모델 ID")
    is_active: bool = Field(..., description="활성 상태")
    is_verified: bool = Field(..., description="인증 상태")
    created_at: datetime = Field(..., description="생성일")
    updated_at: datetime = Field(..., description="수정일")

    class Config:
        from_attributes = True


class ModelList(BaseModel):
    """모델 목록 응답 스키마"""
    models: List[ModelResponse] = Field(..., description="모델 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")


# Portfolio 스키마
class PortfolioBase(BaseModel):
    """포트폴리오 기본 스키마"""
    title: str = Field(..., min_length=2, max_length=200, description="포트폴리오 제목")
    description: Optional[str] = Field(None, max_length=2000, description="설명")
    category: Optional[str] = Field(None, max_length=50, description="카테고리")
    tags: Optional[List[str]] = Field(None, description="태그 목록")
    is_public: bool = Field(True, description="공개 여부")


class PortfolioCreate(PortfolioBase):
    """포트폴리오 생성 스키마"""
    model_id: str = Field(..., description="모델 ID")


class PortfolioUpdate(BaseModel):
    """포트폴리오 수정 스키마"""
    title: Optional[str] = Field(None, min_length=2, max_length=200, description="포트폴리오 제목")
    description: Optional[str] = Field(None, max_length=2000, description="설명")
    category: Optional[str] = Field(None, max_length=50, description="카테고리")
    tags: Optional[List[str]] = Field(None, description="태그 목록")
    is_public: Optional[bool] = Field(None, description="공개 여부")
    is_featured: Optional[bool] = Field(None, description="추천 여부")


class PortfolioResponse(PortfolioBase):
    """포트폴리오 응답 스키마"""
    id: str = Field(..., description="포트폴리오 ID")
    model_id: str = Field(..., description="모델 ID")
    image_urls: Optional[List[str]] = Field(None, description="이미지 URL 목록")
    video_urls: Optional[List[str]] = Field(None, description="비디오 URL 목록")
    is_featured: bool = Field(..., description="추천 여부")
    created_at: datetime = Field(..., description="생성일")
    updated_at: datetime = Field(..., description="수정일")

    class Config:
        from_attributes = True


class PortfolioList(BaseModel):
    """포트폴리오 목록 응답 스키마"""
    portfolios: List[PortfolioResponse] = Field(..., description="포트폴리오 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
