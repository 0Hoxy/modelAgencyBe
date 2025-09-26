"""
모델(인물) 관련 API 라우터
"""
import uuid
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.exceptions import convert_to_http_exception, ApplicationError
from app.domains.models.services import model_service
from app.domains.models.schemas import CreateDomesticModel, CreateOverseaModel, UpdateModel, ReadDomesticModel, \
    ReadOverseaModel, CreateModelResponse

router = APIRouter(prefix="/models", tags=["모델 관리"])


# --- 국내 모델 API ---
@router.post("/domestic", response_model=CreateModelResponse, status_code=201)
async def create_domestic_model(
    model_data: CreateDomesticModel,
    db: AsyncSession = Depends(get_db)
):
    """새로운 국내 모델을 등록합니다."""
    try:
        return await model_service.create_domestic_model(db, model_data)
    except ApplicationError as e:
        raise convert_to_http_exception(e)

# --- 해외 모델 API ---
@router.post("/oversea", response_model=CreateModelResponse, status_code=201)
async def create_oversea_model(
    model_data: CreateOverseaModel,
    db: AsyncSession = Depends(get_db)
):
    """새로운 해외 모델을 등록합니다."""
    try:
        return await model_service.create_oversea_model(db, model_data)
    except ApplicationError as e:
        raise convert_to_http_exception(e)


@router.get("/domestic/{model_id}", response_model=ReadDomesticModel)
async def get_domestic_model(
    model_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """ID로 특정 국내 모델을 조회합니다."""
    try:
        return await model_service.get_domestic_model_by_id(db, model_id)
    except ApplicationError as e:
        raise convert_to_http_exception(e)

@router.get("/oversea/{model_id}", response_model=ReadOverseaModel)
async def get_oversea_model(
    model_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """ID로 특정 해외 모델을 조회합니다."""
    try:
        return await model_service.get_oversea_model_by_id(db, model_id)
    except ApplicationError as e:
        raise convert_to_http_exception(e)


@router.get("/domestic", response_model=List[ReadDomesticModel])
async def get_domestic_models(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(20, ge=1, le=100, description="가져올 항목 수 (최대 100)"),
    db: AsyncSession = Depends(get_db)
):
    """국내 모델 목록을 조회합니다."""
    try:
        return await model_service.get_domestic_models(db, skip=skip, limit=limit)
    except ApplicationError as e:
        raise convert_to_http_exception(e)

@router.get("/oversea", response_model=List[ReadOverseaModel])
async def get_oversea_models(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(20, ge=1, le=100, description="가져올 항목 수 (최대 100)"),
    db: AsyncSession = Depends(get_db)
):
    """해외 모델 목록을 조회합니다."""
    try:
        return await model_service.get_oversea_models(db, skip=skip, limit=limit)
    except ApplicationError as e:
        raise convert_to_http_exception(e)


@router.put("/domestic/{model_id}", response_model=ReadDomesticModel)
async def update_domestic_model(
    model_id: uuid.UUID,
    update_data: UpdateModel,
    db: AsyncSession = Depends(get_db)
):
    """국내 모델 정보를 업데이트합니다."""
    try:
        return await model_service.update_domestic_model(db, model_id, update_data)
    except ApplicationError as e:
        raise convert_to_http_exception(e)

@router.put("/oversea/{model_id}", response_model=ReadOverseaModel)
async def update_oversea_model(
    model_id: uuid.UUID,
    update_data: UpdateModel,
    db: AsyncSession = Depends(get_db)
):
    """해외 모델 정보를 업데이트합니다."""
    try:
        return await model_service.update_oversea_model(db, model_id, update_data)
    except ApplicationError as e:
        raise convert_to_http_exception(e)


@router.delete("/domestic/{model_id}", status_code=204)
async def delete_domestic_model(
    model_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """국내 모델을 삭제합니다."""
    try:
        await model_service.delete_domestic_model(db, model_id)
    except ApplicationError as e:
        raise convert_to_http_exception(e)

@router.delete("/oversea/{model_id}", status_code=204)
async def delete_oversea_model(
    model_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """해외 모델을 삭제합니다."""
    try:
        await model_service.delete_oversea_model(db, model_id)
    except ApplicationError as e:
        raise convert_to_http_exception(e)

#--- 카메라 테스트 ---
