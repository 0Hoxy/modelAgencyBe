"""
관리자 도메인 Service
- 모델 검색 및 관리
- 카메라 테스트 관리
- 대시보드 통계
"""
from datetime import date, datetime, timedelta
from typing import List
from fastapi import HTTPException

from app.core.db import db
from app.domain.admins.admins_repository import admins_repository
from app.domain.admins.admins_schemas import (
    ModelSearchParams,
    PhysicalSizeResponse,
    CameraTestCreate,
    CameraTestStatusUpdate,
    CameraTestResponse,
    CameraTestStatus,
    DashboardResponse,
    DashboardSummary,
    DashboardWeeklyStats,
    DashboardMonthlyStats,
    DailyRegistration,
)
from app.domain.models.models_schemas import ReadDomesticModel, ReadGlobalModel


class AdminsService:
    def __init__(self):
        self.repository = admins_repository

    # ===== 모델 검색 =====

    async def search_domestic_models(
        self,
        search_params: ModelSearchParams
    ) -> dict:
        """
        국내 모델 검색
        """
        try:
            # 검색 결과 조회
            models = await self.repository.search_models(search_params, is_foreigner=False)
            
            # 총 개수 조회
            total_count = await self.repository.count_models(search_params, is_foreigner=False)
            
            # Pydantic 모델로 변환
            model_list = [ReadDomesticModel.model_validate(dict(model)) for model in models]
            
            return {
                "total_count": total_count,
                "page": search_params.page,
                "page_size": search_params.page_size,
                "total_pages": (total_count + search_params.page_size - 1) // search_params.page_size,
                "models": model_list,
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"국내 모델 검색 중 오류가 발생했습니다: {str(e)}"
            )

    async def search_global_models(
        self,
        search_params: ModelSearchParams
    ) -> dict:
        """
        해외 모델 검색
        """
        try:
            # 검색 결과 조회
            models = await self.repository.search_models(search_params, is_foreigner=True)
            
            # 총 개수 조회
            total_count = await self.repository.count_models(search_params, is_foreigner=True)
            
            # Pydantic 모델로 변환
            model_list = [ReadGlobalModel.model_validate(dict(model)) for model in models]
            
            return {
                "total_count": total_count,
                "page": search_params.page,
                "page_size": search_params.page_size,
                "total_pages": (total_count + search_params.page_size - 1) // search_params.page_size,
                "models": model_list,
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"해외 모델 검색 중 오류가 발생했습니다: {str(e)}"
            )

    # ===== 신체 사이즈 조회 =====

    async def get_physical_size(self, model_id: int) -> PhysicalSizeResponse:
        """
        모델 신체 사이즈 조회
        """
        try:
            result = await self.repository.get_physical_size(model_id)
            
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"ID {model_id}인 모델을 찾을 수 없습니다."
                )
            
            return PhysicalSizeResponse.model_validate(dict(result))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"신체 사이즈 조회 중 오류가 발생했습니다: {str(e)}"
            )

    # ===== 카메라 테스트 관리 =====

    async def create_camera_test(
        self,
        request: CameraTestCreate
    ) -> CameraTestResponse:
        """
        카메라 테스트 등록
        - 현재 시간을 기준으로 등록
        """
        try:
            # 이미 등록된 카메라 테스트가 있는지 확인
            existing = await self.repository.get_camera_test(request.model_id)
            if existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"모델 ID {request.model_id}는 이미 카메라 테스트에 등록되어 있습니다."
                )
            
            # 현재 시간으로 등록
            visited_at = datetime.now()
            
            async with db.transaction() as conn:
                result = await self.repository.create_camera_test_transaction(
                    conn=conn,
                    model_id=request.model_id,
                    visited_at=visited_at
                )
            
            return CameraTestResponse.model_validate(dict(result))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"카메라 테스트 등록 중 오류가 발생했습니다: {str(e)}"
            )

    async def update_camera_test_status(
        self,
        model_id: int,
        request: CameraTestStatusUpdate
    ) -> CameraTestResponse:
        """
        카메라 테스트 상태 변경
        - 준비중 → 테스트중 → 완료
        """
        try:
            # 카메라 테스트가 등록되어 있는지 확인
            existing = await self.repository.get_camera_test(model_id)
            if not existing:
                raise HTTPException(
                    status_code=404,
                    detail=f"모델 ID {model_id}의 카메라 테스트를 찾을 수 없습니다."
                )
            
            async with db.transaction() as conn:
                result = await self.repository.update_camera_test_status_transaction(
                    conn=conn,
                    model_id=model_id,
                    status=request.status
                )
            
            if not result:
                raise HTTPException(
                    status_code=500,
                    detail="카메라 테스트 상태 변경에 실패했습니다."
                )
            
            return CameraTestResponse.model_validate(dict(result))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"카메라 테스트 상태 변경 중 오류가 발생했습니다: {str(e)}"
            )

    # ===== 대시보드 통계 =====

    async def get_dashboard_stats(self) -> DashboardResponse:
        """
        대시보드 통계 조회
        - 요약 정보
        - 주간 통계 (최근 7일)
        - 월간 통계 (최근 30일)
        """
        try:
            # 1. 요약 정보
            today_registrations = await self.repository.get_today_registrations_count()
            today_incomplete_camera_tests = await self.repository.get_today_incomplete_camera_tests_count()
            incomplete_addresses = await self.repository.get_incomplete_addresses_count()
            
            summary = DashboardSummary(
                today_registrations=today_registrations,
                today_incomplete_camera_tests=today_incomplete_camera_tests,
                incomplete_addresses=incomplete_addresses,
            )
            
            # 2. 주간 통계 (최근 7일)
            today = date.today()
            week_start = today - timedelta(days=6)  # 오늘 포함 7일
            weekly_data = await self.repository.get_daily_registrations(week_start, today)
            
            # 날짜별로 매핑 (데이터가 없는 날짜는 0으로)
            weekly_map = {row["date"]: row["count"] for row in weekly_data}
            weekly_registrations = [
                DailyRegistration(
                    date=week_start + timedelta(days=i),
                    count=weekly_map.get(week_start + timedelta(days=i), 0)
                )
                for i in range(7)
            ]
            
            weekly_stats = DashboardWeeklyStats(daily_registrations=weekly_registrations)
            
            # 3. 월간 통계 (최근 30일)
            month_start = today - timedelta(days=29)  # 오늘 포함 30일
            monthly_data = await self.repository.get_daily_registrations(month_start, today)
            
            # 날짜별로 매핑
            monthly_map = {row["date"]: row["count"] for row in monthly_data}
            monthly_registrations = [
                DailyRegistration(
                    date=month_start + timedelta(days=i),
                    count=monthly_map.get(month_start + timedelta(days=i), 0)
                )
                for i in range(30)
            ]
            
            monthly_stats = DashboardMonthlyStats(daily_registrations=monthly_registrations)
            
            return DashboardResponse(
                summary=summary,
                weekly_stats=weekly_stats,
                monthly_stats=monthly_stats,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"대시보드 통계 조회 중 오류가 발생했습니다: {str(e)}"
            )


# Singleton 인스턴스
admins_service = AdminsService()
