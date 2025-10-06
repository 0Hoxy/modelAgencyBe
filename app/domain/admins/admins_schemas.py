"""
관리자 도메인 스키마
- 모델 검색
- 카메라 테스트
- 대시보드
"""
from datetime import date, datetime
from typing import Optional
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


# ===== 카메라 테스트 관련 =====

class CameraTestStatus(str, Enum):
    """카메라 테스트 상태 (DB enum camerateststatusenum과 매핑)"""
    PENDING = "PENDING"      # 대기
    CONFIRMED = "CONFIRMED"  # 확정/진행중
    COMPLETED = "COMPLETED"  # 완료
    CANCELLED = "CANCELLED"  # 취소

    def to_korean(self) -> str:
        """한글 변환"""
        mapping = {
            "PENDING": "대기",
            "CONFIRMED": "확정",
            "COMPLETED": "완료",
            "CANCELLED": "취소",
        }
        return mapping.get(self.value, self.value)


class CameraTestCreate(BaseModel):
    """카메라 테스트 등록 요청"""
    model_id: UUID = Field(..., description="모델 ID")


class CameraTestStatusUpdate(BaseModel):
    """카메라 테스트 상태 변경 요청"""
    status: CameraTestStatus = Field(..., description="변경할 상태")


class CameraTestResponse(BaseModel):
    """카메라 테스트 응답"""
    id: int
    model_id: UUID
    is_tested: CameraTestStatus
    visited_at: datetime

    class Config:
        from_attributes = True


# ===== 모델 검색 관련 =====

class ModelSearchParams(BaseModel):
    """모델 검색 조건"""
    name: Optional[str] = Field(None, description="이름 (부분 검색)")
    gender: Optional[str] = Field(None, description="성별")
    address_city: Optional[str] = Field(None, description="주소 (시)")
    address_district: Optional[str] = Field(None, description="주소 (구)")
    special_abilities: Optional[str] = Field(None, description="특기 (부분 검색)")
    other_languages: Optional[str] = Field(None, description="가능한 외국어 (부분 검색)")
    korean_level: Optional[str] = Field(None, description="한국어 수준 (해외 모델)")
    
    # 페이징
    page: int = Field(default=1, ge=1, description="페이지 번호")
    page_size: int = Field(default=20, ge=1, le=100, description="페이지 크기")


# ===== 신체 사이즈 관련 =====

class PhysicalSizeResponse(BaseModel):
    """모델 신체 사이즈 응답"""
    model_id: UUID
    name: str
    height: Optional[float] = None
    weight: Optional[float] = None
    top_size: Optional[str] = None
    bottom_size: Optional[str] = None
    shoes_size: Optional[str] = None

    class Config:
        from_attributes = True


# ===== 대시보드 관련 =====

class DailyRegistration(BaseModel):
    """일별 등록 통계"""
    date: date
    count: int


class DashboardWeeklyStats(BaseModel):
    """주간 대시보드 통계"""
    daily_registrations: list[DailyRegistration] = Field(..., description="일별 등록 인원 (최근 7일)")
    

class DashboardMonthlyStats(BaseModel):
    """월간 대시보드 통계"""
    daily_registrations: list[DailyRegistration] = Field(..., description="일별 등록 인원 (최근 30일)")


class DashboardSummary(BaseModel):
    """대시보드 요약 정보"""
    today_registrations: int = Field(..., description="금일 등록 모델 수")
    today_incomplete_camera_tests: int = Field(..., description="금일 카메라테스트 미완료 인원")
    incomplete_addresses: int = Field(..., description="주소록 등록 미완료 인원")


class DashboardResponse(BaseModel):
    """대시보드 전체 응답"""
    summary: DashboardSummary
    weekly_stats: DashboardWeeklyStats
    monthly_stats: DashboardMonthlyStats
