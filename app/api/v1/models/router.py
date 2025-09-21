"""
모델 관리 API 라우터
모델 등록, 조회, 수정, 삭제 등
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.core.dependencies import get_current_user, get_admin_user
from app.schemas.model import ModelCreate, ModelUpdate, ModelResponse, ModelListResponse

# 모델 라우터 생성
models_router = APIRouter()


@models_router.get("/", response_model=ModelListResponse)
async def get_models(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(10, ge=1, le=100, description="가져올 개수"),
    search: Optional[str] = Query(None, description="검색어"),
    category: Optional[str] = Query(None, description="카테고리"),
    current_user: dict = Depends(get_current_user)
):
    """
    모델 목록 조회 (페이징, 검색, 필터링)
    """
    # TODO: 실제 모델 목록 조회 로직 구현
    
    return ModelListResponse(
        models=[],
        total=0,
        skip=skip,
        limit=limit
    )


@models_router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    특정 모델 상세 조회
    """
    # TODO: 실제 모델 조회 로직 구현
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="모델을 찾을 수 없습니다"
    )


@models_router.post("/", response_model=ModelResponse)
async def create_model(
    model_data: ModelCreate,
    current_user: dict = Depends(get_admin_user)
):
    """
    새 모델 등록 (관리자만)
    """
    # TODO: 실제 모델 생성 로직 구현
    
    return ModelResponse(
        model_id="temp_model_id",
        name=model_data.name,
        description=model_data.description,
        category=model_data.category,
        price_per_hour=model_data.price_per_hour,
        is_available=True,
        created_at="2024-01-01T00:00:00Z"
    )


@models_router.put("/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: str,
    model_data: ModelUpdate,
    current_user: dict = Depends(get_admin_user)
):
    """
    모델 정보 수정 (관리자만)
    """
    # TODO: 실제 모델 수정 로직 구현
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="모델을 찾을 수 없습니다"
    )


@models_router.delete("/{model_id}")
async def delete_model(
    model_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """
    모델 삭제 (관리자만)
    """
    # TODO: 실제 모델 삭제 로직 구현
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="모델을 찾을 수 없습니다"
    )


@models_router.post("/{model_id}/toggle-availability")
async def toggle_model_availability(
    model_id: str,
    current_user: dict = Depends(get_admin_user)
):
    """
    모델 예약 가능 상태 토글 (관리자만)
    """
    # TODO: 실제 모델 상태 변경 로직 구현
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="모델을 찾을 수 없습니다"
    )
