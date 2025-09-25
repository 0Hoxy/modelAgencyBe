"""
모델(인물) 관련 API 라우터
"""
import uuid
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Union

from app.core.database import get_db
from app.core.exceptions import convert_to_http_exception, ApplicationError
from app.domains.models.services import model_service
from app.domains.models.schemas import CreateDomesticModel, CreateOverseaModel, UpdateModel, ReadDomesticModel, \
    ReadOverseaModel, CreateModelResponse

router = APIRouter(prefix="/models", tags=["모델 관리"])


@router.post("/", response_model=CreateModelResponse, status_code=201)
async def create_model(
    model_data: CreateDomesticModel | CreateOverseaModel,
    db: AsyncSession = Depends(get_db)
):
    """새로운 모델을 등록합니다."""
    try:
        return await model_service.create_model(db, model_data)
    except ApplicationError as e:
        raise convert_to_http_exception(e)


@router.get("/{model_id}", response_model=Union[ReadDomesticModel, ReadOverseaModel])
async def get_model(
    model_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """ID로 특정 모델을 조회합니다."""
    try:
        return await model_service.get_model_by_id(db, model_id)
    except ApplicationError as e:
        raise convert_to_http_exception(e)


@router.get("/", response_model=List[Union[ReadDomesticModel, ReadOverseaModel]])
async def get_models(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(20, ge=1, le=100, description="가져올 항목 수 (최대 100)"),
    db: AsyncSession = Depends(get_db)
):
    """모델 목록을 조회합니다."""
    try:
        return await model_service.get_models(db, skip=skip, limit=limit)
    except ApplicationError as e:
        raise convert_to_http_exception(e)


@router.put("/{model_id}", response_model=Union[ReadDomesticModel, ReadOverseaModel])
async def update_model(
    model_id: uuid.UUID,
    update_data: UpdateModel,
    db: AsyncSession = Depends(get_db)
):
    """모델 정보를 업데이트합니다."""
    try:
        return await model_service.update_model(db, model_id, update_data)
    except ApplicationError as e:
        raise convert_to_http_exception(e)


@router.delete("/{model_id}", status_code=204)
async def delete_model(
    model_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """모델을 삭제합니다."""
    try:
        await model_service.delete_model(db, model_id)
    except ApplicationError as e:
        raise convert_to_http_exception(e)