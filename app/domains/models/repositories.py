"""
모델(인물) 관련 데이터 접근 계층
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
import uuid

from .models import Model, Portfolio
from .schemas import ModelCreate, ModelUpdate, PortfolioCreate, PortfolioUpdate


class ModelRepository:
    """모델 리포지토리"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, model_data: ModelCreate) -> Model:
        """모델 생성"""
        db_model = Model(**model_data.model_dump())
        self.db.add(db_model)
        await self.db.commit()
        await self.db.refresh(db_model)
        return db_model

    async def get_by_id(self, model_id: str) -> Optional[Model]:
        """ID로 모델 조회"""
        result = await self.db.execute(
            select(Model).where(Model.id == model_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[Model]:
        """이메일로 모델 조회"""
        result = await self.db.execute(
            select(Model).where(Model.email == email)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 10,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None
    ) -> List[Model]:
        """모델 목록 조회"""
        query = select(Model)
        
        if is_active is not None:
            query = query.where(Model.is_active == is_active)
        if is_verified is not None:
            query = query.where(Model.is_verified == is_verified)
            
        query = query.offset(skip).limit(limit).order_by(Model.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def count(
        self,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None
    ) -> int:
        """모델 개수 조회"""
        query = select(Model.id)
        
        if is_active is not None:
            query = query.where(Model.is_active == is_active)
        if is_verified is not None:
            query = query.where(Model.is_verified == is_verified)
            
        result = await self.db.execute(query)
        return len(result.scalars().all())

    async def update(self, model_id: str, model_data: ModelUpdate) -> Optional[Model]:
        """모델 수정"""
        update_data = model_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(model_id)
            
        await self.db.execute(
            update(Model)
            .where(Model.id == model_id)
            .values(**update_data)
        )
        await self.db.commit()
        return await self.get_by_id(model_id)

    async def delete(self, model_id: str) -> bool:
        """모델 삭제"""
        result = await self.db.execute(
            delete(Model).where(Model.id == model_id)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def search(
        self,
        query: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[Model]:
        """모델 검색"""
        search_query = select(Model).where(
            Model.name.ilike(f"%{query}%") |
            Model.bio.ilike(f"%{query}%") |
            Model.experience.ilike(f"%{query}%")
        ).offset(skip).limit(limit).order_by(Model.created_at.desc())
        
        result = await self.db.execute(search_query)
        return result.scalars().all()


class PortfolioRepository:
    """포트폴리오 리포지토리"""
    
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, portfolio_data: PortfolioCreate) -> Portfolio:
        """포트폴리오 생성"""
        db_portfolio = Portfolio(**portfolio_data.model_dump())
        self.db.add(db_portfolio)
        await self.db.commit()
        await self.db.refresh(db_portfolio)
        return db_portfolio

    async def get_by_id(self, portfolio_id: str) -> Optional[Portfolio]:
        """ID로 포트폴리오 조회"""
        result = await self.db.execute(
            select(Portfolio).where(Portfolio.id == portfolio_id)
        )
        return result.scalar_one_or_none()

    async def get_by_model_id(
        self,
        model_id: str,
        skip: int = 0,
        limit: int = 10,
        is_public: Optional[bool] = None
    ) -> List[Portfolio]:
        """모델 ID로 포트폴리오 목록 조회"""
        query = select(Portfolio).where(Portfolio.model_id == model_id)
        
        if is_public is not None:
            query = query.where(Portfolio.is_public == is_public)
            
        query = query.offset(skip).limit(limit).order_by(Portfolio.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_featured(self, limit: int = 10) -> List[Portfolio]:
        """추천 포트폴리오 조회"""
        result = await self.db.execute(
            select(Portfolio)
            .where(Portfolio.is_featured == True)
            .where(Portfolio.is_public == True)
            .limit(limit)
            .order_by(Portfolio.created_at.desc())
        )
        return result.scalars().all()

    async def count_by_model_id(
        self,
        model_id: str,
        is_public: Optional[bool] = None
    ) -> int:
        """모델의 포트폴리오 개수 조회"""
        query = select(Portfolio.id).where(Portfolio.model_id == model_id)
        
        if is_public is not None:
            query = query.where(Portfolio.is_public == is_public)
            
        result = await self.db.execute(query)
        return len(result.scalars().all())

    async def update(self, portfolio_id: str, portfolio_data: PortfolioUpdate) -> Optional[Portfolio]:
        """포트폴리오 수정"""
        update_data = portfolio_data.model_dump(exclude_unset=True)
        if not update_data:
            return await self.get_by_id(portfolio_id)
            
        await self.db.execute(
            update(Portfolio)
            .where(Portfolio.id == portfolio_id)
            .values(**update_data)
        )
        await self.db.commit()
        return await self.get_by_id(portfolio_id)

    async def delete(self, portfolio_id: str) -> bool:
        """포트폴리오 삭제"""
        result = await self.db.execute(
            delete(Portfolio).where(Portfolio.id == portfolio_id)
        )
        await self.db.commit()
        return result.rowcount > 0
