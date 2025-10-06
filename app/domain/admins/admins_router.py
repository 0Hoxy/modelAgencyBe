"""
관리자 도메인 라우터
- 모델 검색 및 관리
- 카메라 테스트 관리
- 대시보드 통계
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from datetime import date

from app.shared import require_admin, require_admin_or_director
from app.domain.models.models_services import models_services
from app.domain.models.models_schemas import CreateDomesticModel, CreateGlobalModel, UpdateDomesticModel, UpdateGlobalModel
from app.domain.admins.admins_service import admins_service
from app.domain.admins.admins_schemas import (
    ModelSearchParams,
    PhysicalSizeResponse,
    CameraTestCreate,
    CameraTestStatusUpdate,
    CameraTestResponse,
    DashboardResponse,
)


app = APIRouter(
    prefix="/admins",
    tags=["admins"],
    responses={404: {"description": "Not found"}},
)


# ===== 모델 검색 (관리자 전용) =====

@app.get("/models/domestic")
async def search_domestic_models(
    name: str = Query(None, description="이름 (부분 검색)"),
    gender: str = Query(None, description="성별"),
    address_city: str = Query(None, description="주소 (시)"),
    address_district: str = Query(None, description="주소 (구)"),
    special_abilities: str = Query(None, description="특기"),
    other_languages: str = Query(None, description="가능한 외국어"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    current_user: dict = Depends(require_admin)
):
    """
    국내 모델 리스트 조회 (검색 조건 포함)
    - 관리자 권한 필요
    """
    search_params = ModelSearchParams(
        name=name,
        gender=gender,
        address_city=address_city,
        address_district=address_district,
        special_abilities=special_abilities,
        other_languages=other_languages,
        page=page,
        page_size=page_size,
    )
    return await admins_service.search_domestic_models(search_params)


@app.get("/models/global")
async def search_global_models(
    name: str = Query(None, description="이름 (부분 검색)"),
    gender: str = Query(None, description="성별"),
    address_city: str = Query(None, description="주소 (시)"),
    address_district: str = Query(None, description="주소 (구)"),
    special_abilities: str = Query(None, description="특기"),
    other_languages: str = Query(None, description="가능한 외국어"),
    korean_level: str = Query(None, description="한국어 수준"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    current_user: dict = Depends(require_admin)
):
    """
    해외 모델 리스트 조회 (검색 조건 포함)
    - 관리자 권한 필요
    """
    search_params = ModelSearchParams(
        name=name,
        gender=gender,
        address_city=address_city,
        address_district=address_district,
        special_abilities=special_abilities,
        other_languages=other_languages,
        korean_level=korean_level,
        page=page,
        page_size=page_size,
    )
    return await admins_service.search_global_models(search_params)


# ===== 모델 등록 (관리자) =====

@app.post("/models/domestic")
async def create_domestic_model(
    request: CreateDomesticModel,
    current_user: dict = Depends(require_admin)
):
    """
    국내 모델 등록
    - 관리자 권한 필요
    """
    return await models_services.create_domestic_model(request)


@app.post("/models/global")
async def create_global_model(
    request: CreateGlobalModel,
    current_user: dict = Depends(require_admin)
):
    """
    해외 모델 등록
    - 관리자 권한 필요
    """
    return await models_services.create_foreign_model(request)


# ===== 모델 수정 (관리자) =====

@app.put("/models/domestic")
async def update_domestic_model(
    request: UpdateDomesticModel,
    current_user: dict = Depends(require_admin)
):
    """
    국내 모델 정보 수정
    - 관리자 권한 필요
    """
    return await models_services.update_domestic_model(request)


@app.put("/models/global")
async def update_global_model(
    request: UpdateGlobalModel,
    current_user: dict = Depends(require_admin)
):
    """
    해외 모델 정보 수정
    - 관리자 권한 필요
    """
    return await models_services.update_foreign_model(request)


# ===== 모델 신체 사이즈 조회 (관리자 전용) =====

@app.get("/models/{model_id}/physical", response_model=PhysicalSizeResponse)
async def get_physical_size(
    model_id: UUID,
    current_user: dict = Depends(require_admin)
):
    """
    모델 신체 사이즈 조회
    - 관리자 권한 필요
    """
    return await admins_service.get_physical_size(model_id)


# ===== 카메라 테스트 관리 (관리자/디렉터) =====

@app.post("/models/cameraTest", response_model=CameraTestResponse)
async def create_camera_test(
    request: CameraTestCreate,
    current_user: dict = Depends(require_admin_or_director)
):
    """
    기존 등록 모델 카메라 테스트 등록
    - 현재 시간 기준으로 등록
    - 관리자 또는 디렉터 권한 필요
    """
    return await admins_service.create_camera_test(request)


@app.put("/models/{model_id}/cameraTest", response_model=CameraTestResponse)
async def update_camera_test_status(
    model_id: UUID,
    request: CameraTestStatusUpdate,
    current_user: dict = Depends(require_admin_or_director)
):
    """
    카메라 테스트 상태 변경
    - 준비중 → 테스트중 → 완료
    - 관리자 또는 디렉터 권한 필요
    """
    return await admins_service.update_camera_test_status(model_id, request)


# ===== 대시보드 (관리자/디렉터) =====

@app.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    current_user: dict = Depends(require_admin_or_director)
):
    """
    대시보드 정보 조회
    - 요약 정보: 금일 등록, 카메라테스트 미완료, 주소록 미완료
    - 주간 통계: 최근 7일 일별 등록 인원
    - 월간 통계: 최근 30일 일별 등록 인원
    - 관리자 또는 디렉터 권한 필요
    """
    return await admins_service.get_dashboard_stats()

@app.get("/models/cameraTest")
async def get_camera_test(
    target_date: date | None = Query(None, description="YYYY-MM-DD. 미전송 시 오늘 기준"),
    current_user: dict = Depends(require_admin_or_director)
):
    """
    카메라테스트 목록 조회
    - 관리자 또는 디렉터 권한 필요
    - 특정 날짜(target_date)의 카메라테스트를 모델당 1건(가장 이른 방문)으로 그룹핑하여 시간 오름차순 반환
    """
    return await admins_service.get_camera_test(target_date)