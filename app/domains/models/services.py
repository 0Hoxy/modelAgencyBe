"""
모델(인물) 관련 비즈니스 로직
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from .repositories import ModelRepository, PortfolioRepository
from .schemas import (
    ModelCreate, ModelUpdate, ModelResponse, ModelList,
    PortfolioCreate, PortfolioUpdate, PortfolioResponse, PortfolioList
)
from app.core.exceptions import ModelNotFoundException, ValidationException


class ModelService:
    """모델 서비스"""
    
    def __init__(self, db: AsyncSession):
        self.model_repo = ModelRepository(db)

    async def create_model(self, model_data: ModelCreate) -> ModelResponse:
        """모델 생성"""
        # 이메일 중복 검사
        existing_model = await self.model_repo.get_by_email(model_data.email)
        if existing_model:
            raise ValidationException("이미 존재하는 이메일입니다")

        # 모델 생성
        model = await self.model_repo.create(model_data)
        return ModelResponse.model_validate(model)

    async def get_model_by_id(self, model_id: str) -> ModelResponse:
        """모델 조회"""
        model = await self.model_repo.get_by_id(model_id)
        if not model:
            raise ModelNotFoundException(model_id)
        return ModelResponse.model_validate(model)

    async def get_models(
        self,
        page: int = 1,
        size: int = 10,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None
    ) -> ModelList:
        """모델 목록 조회"""
        skip = (page - 1) * size
        
        models = await self.model_repo.get_all(
            skip=skip,
            limit=size,
            is_active=is_active,
            is_verified=is_verified
        )
        
        total = await self.model_repo.count(
            is_active=is_active,
            is_verified=is_verified
        )
        
        model_responses = [ModelResponse.model_validate(model) for model in models]
        
        return ModelList(
            models=model_responses,
            total=total,
            page=page,
            size=size
        )

    async def update_model(self, model_id: str, model_data: ModelUpdate) -> ModelResponse:
        """모델 수정"""
        model = await self.model_repo.get_by_id(model_id)
        if not model:
            raise ModelNotFoundException(model_id)

        # 이메일 변경 시 중복 검사
        if model_data.email and model_data.email != model.email:
            existing_model = await self.model_repo.get_by_email(model_data.email)
            if existing_model:
                raise ValidationException("이미 존재하는 이메일입니다")

        updated_model = await self.model_repo.update(model_id, model_data)
        if not updated_model:
            raise ModelNotFoundException(model_id)
            
        return ModelResponse.model_validate(updated_model)

    async def delete_model(self, model_id: str) -> bool:
        """모델 삭제"""
        model = await self.model_repo.get_by_id(model_id)
        if not model:
            raise ModelNotFoundException(model_id)

        return await self.model_repo.delete(model_id)

    async def search_models(
        self,
        query: str,
        page: int = 1,
        size: int = 10
    ) -> ModelList:
        """모델 검색"""
        if not query or len(query.strip()) < 2:
            raise ValidationException("검색어는 2글자 이상이어야 합니다")

        skip = (page - 1) * size
        
        models = await self.model_repo.search(
            query=query.strip(),
            skip=skip,
            limit=size
        )
        
        # 검색 결과 개수는 정확하지 않을 수 있으므로 실제 결과 개수 사용
        total = len(models)
        
        model_responses = [ModelResponse.model_validate(model) for model in models]
        
        return ModelList(
            models=model_responses,
            total=total,
            page=page,
            size=size
        )


class PortfolioService:
    """포트폴리오 서비스"""
    
    def __init__(self, db: AsyncSession):
        self.portfolio_repo = PortfolioRepository(db)
        self.model_repo = ModelRepository(db)

    async def create_portfolio(self, portfolio_data: PortfolioCreate) -> PortfolioResponse:
        """포트폴리오 생성"""
        # 모델 존재 여부 확인
        model = await self.model_repo.get_by_id(portfolio_data.model_id)
        if not model:
            raise ModelNotFoundException(portfolio_data.model_id)

        # 포트폴리오 생성
        portfolio = await self.portfolio_repo.create(portfolio_data)
        return PortfolioResponse.model_validate(portfolio)

    async def get_portfolio_by_id(self, portfolio_id: str) -> PortfolioResponse:
        """포트폴리오 조회"""
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if not portfolio:
            raise ModelNotFoundException(portfolio_id)
        return PortfolioResponse.model_validate(portfolio)

    async def get_portfolios_by_model_id(
        self,
        model_id: str,
        page: int = 1,
        size: int = 10,
        is_public: Optional[bool] = None
    ) -> PortfolioList:
        """모델의 포트폴리오 목록 조회"""
        # 모델 존재 여부 확인
        model = await self.model_repo.get_by_id(model_id)
        if not model:
            raise ModelNotFoundException(model_id)

        skip = (page - 1) * size
        
        portfolios = await self.portfolio_repo.get_by_model_id(
            model_id=model_id,
            skip=skip,
            limit=size,
            is_public=is_public
        )
        
        total = await self.portfolio_repo.count_by_model_id(
            model_id=model_id,
            is_public=is_public
        )
        
        portfolio_responses = [PortfolioResponse.model_validate(portfolio) for portfolio in portfolios]
        
        return PortfolioList(
            portfolios=portfolio_responses,
            total=total,
            page=page,
            size=size
        )

    async def get_featured_portfolios(self, limit: int = 10) -> List[PortfolioResponse]:
        """추천 포트폴리오 조회"""
        portfolios = await self.portfolio_repo.get_featured(limit=limit)
        return [PortfolioResponse.model_validate(portfolio) for portfolio in portfolios]

    async def update_portfolio(self, portfolio_id: str, portfolio_data: PortfolioUpdate) -> PortfolioResponse:
        """포트폴리오 수정"""
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if not portfolio:
            raise ModelNotFoundException(portfolio_id)

        updated_portfolio = await self.portfolio_repo.update(portfolio_id, portfolio_data)
        if not updated_portfolio:
            raise ModelNotFoundException(portfolio_id)
            
        return PortfolioResponse.model_validate(updated_portfolio)

    async def delete_portfolio(self, portfolio_id: str) -> bool:
        """포트폴리오 삭제"""
        portfolio = await self.portfolio_repo.get_by_id(portfolio_id)
        if not portfolio:
            raise ModelNotFoundException(portfolio_id)

        return await self.portfolio_repo.delete(portfolio_id)
