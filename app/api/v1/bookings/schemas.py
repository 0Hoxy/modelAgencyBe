"""
예약 관련 Pydantic 스키마
요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BookingCreate(BaseModel):
    """예약 생성 요청 스키마"""
    model_id: str = Field(..., description="모델 ID")
    start_time: datetime = Field(..., description="시작 시간")
    end_time: datetime = Field(..., description="종료 시간")
    total_price: int = Field(..., gt=0, description="총 가격")
    notes: Optional[str] = Field(None, max_length=500, description="특이사항")


class BookingUpdate(BaseModel):
    """예약 수정 요청 스키마"""
    start_time: Optional[datetime] = Field(None, description="시작 시간")
    end_time: Optional[datetime] = Field(None, description="종료 시간")
    total_price: Optional[int] = Field(None, gt=0, description="총 가격")
    notes: Optional[str] = Field(None, max_length=500, description="특이사항")


class BookingResponse(BaseModel):
    """예약 응답 스키마"""
    booking_id: str = Field(..., description="예약 ID")
    model_id: str = Field(..., description="모델 ID")
    client_id: str = Field(..., description="클라이언트 ID")
    start_time: datetime = Field(..., description="시작 시간")
    end_time: datetime = Field(..., description="종료 시간")
    total_price: int = Field(..., description="총 가격")
    status: str = Field(..., description="예약 상태")
    notes: Optional[str] = Field(None, description="특이사항")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: datetime = Field(..., description="수정일시")


class BookingListResponse(BaseModel):
    """예약 목록 응답 스키마"""
    bookings: List[BookingResponse] = Field(..., description="예약 목록")
    total: int = Field(..., description="전체 개수")
    skip: int = Field(..., description="건너뛴 개수")
    limit: int = Field(..., description="가져온 개수")
