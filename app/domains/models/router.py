"""
모델(인물) 관련 API 라우터
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from .services import ModelService, PortfolioService
from .schemas import (
    ModelCreate, ModelUpdate, ModelResponse, ModelList,
    PortfolioCreate, PortfolioUpdate, PortfolioResponse, PortfolioList
)
from app.core.database import get_db
from app.core.exceptions import ModelNotFoundException, ValidationException

router = APIRouter(prefix="/models", tags=["모델 관리"])


# 의존성 주입
def get_model_service(db: AsyncSession = Depends(get_db)) -> ModelService:
    return ModelService(db)


def get_portfolio_service(db: AsyncSession = Depends(get_db)) -> PortfolioService:
    return PortfolioService(db)


# 모델 관련 엔드포인트
@router.post("/", response_model=ModelResponse, status_code=201)
async def create_model(
    model_data: ModelCreate,
    model_service: ModelService = Depends(get_model_service)
):
    """모델 생성"""
    try:
        return await model_service.create_model(model_data)
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=ModelList)
async def get_models(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    is_active: Optional[bool] = Query(None, description="활성 상태 필터"),
    is_verified: Optional[bool] = Query(None, description="인증 상태 필터"),
    model_service: ModelService = Depends(get_model_service)
):
    """모델 목록 조회"""
    return await model_service.get_models(
        page=page,
        size=size,
        is_active=is_active,
        is_verified=is_verified
    )


@router.get("/search", response_model=ModelList)
async def search_models(
    q: str = Query(..., min_length=2, description="검색어"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    model_service: ModelService = Depends(get_model_service)
):
    """모델 검색"""
    try:
        return await model_service.search_models(
            query=q,
            page=page,
            size=size
        )
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: str = Path(..., description="모델 ID"),
    model_service: ModelService = Depends(get_model_service)
):
    """모델 상세 조회"""
    try:
        return await model_service.get_model_by_id(model_id)
    except ModelNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{model_id}", response_model=ModelResponse)
async def update_model(
    model_id: str = Path(..., description="모델 ID"),
    model_data: ModelUpdate = ...,
    model_service: ModelService = Depends(get_model_service)
):
    """모델 수정"""
    try:
        return await model_service.update_model(model_id, model_data)
    except ModelNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{model_id}")
async def delete_model(
    model_id: str = Path(..., description="모델 ID"),
    model_service: ModelService = Depends(get_model_service)
):
    """모델 삭제"""
    try:
        success = await model_service.delete_model(model_id)
        if success:
            return {"message": "모델이 삭제되었습니다"}
        else:
            raise HTTPException(status_code=500, detail="모델 삭제에 실패했습니다")
    except ModelNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


# 포트폴리오 관련 엔드포인트
@router.post("/portfolios", response_model=PortfolioResponse, status_code=201)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """포트폴리오 생성"""
    try:
        return await portfolio_service.create_portfolio(portfolio_data)
    except ModelNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/portfolios/featured", response_model=list[PortfolioResponse])
async def get_featured_portfolios(
    limit: int = Query(10, ge=1, le=50, description="조회 개수"),
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """추천 포트폴리오 조회"""
    return await portfolio_service.get_featured_portfolios(limit=limit)


@router.get("/portfolios/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(
    portfolio_id: str = Path(..., description="포트폴리오 ID"),
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """포트폴리오 상세 조회"""
    try:
        return await portfolio_service.get_portfolio_by_id(portfolio_id)
    except ModelNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{model_id}/portfolios", response_model=PortfolioList)
async def get_model_portfolios(
    model_id: str = Path(..., description="모델 ID"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    is_public: Optional[bool] = Query(None, description="공개 여부 필터"),
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """모델의 포트폴리오 목록 조회"""
    try:
        return await portfolio_service.get_portfolios_by_model_id(
            model_id=model_id,
            page=page,
            size=size,
            is_public=is_public
        )
    except ModelNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/portfolios/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(
    portfolio_id: str = Path(..., description="포트폴리오 ID"),
    portfolio_data: PortfolioUpdate = ...,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """포트폴리오 수정"""
    try:
        return await portfolio_service.update_portfolio(portfolio_id, portfolio_data)
    except ModelNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/portfolios/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: str = Path(..., description="포트폴리오 ID"),
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """포트폴리오 삭제"""
    try:
        success = await portfolio_service.delete_portfolio(portfolio_id)
        if success:
            return {"message": "포트폴리오가 삭제되었습니다"}
        else:
            raise HTTPException(status_code=500, detail="포트폴리오 삭제에 실패했습니다")
    except ModelNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
