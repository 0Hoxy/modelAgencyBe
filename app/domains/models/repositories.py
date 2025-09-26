"""
모델(인물) 관련 데이터 접근 계층
"""
import uuid
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.logging import get_repository_logger, log_db_operation
from app.core.exceptions import handle_repository_exceptions, EntityNotFoundError
from app.domains.models.schemas import CreateDomesticModel, CreateOverseaModel, UpdateModel
from app.domains.models.models import Model


class ModelRepository:
    def __init__(self):
        """Repository 초기화"""
        self.logger = get_repository_logger("model")

    @log_db_operation("CREATE")
    @handle_repository_exceptions
    async def create_domestic(self, db: AsyncSession, model_data: CreateDomesticModel) -> Model:
        """새로운 모델을 생성합니다."""
        model = Model(**model_data.model_dump(), is_foreigner=False)
        self.logger.debug(f"모델 생성 데이터: {model_data.model_dump()}")
        db.add(model)
        await db.commit()
        await db.refresh(model)
        self.logger.info(f"모델 생성 성공 - ID: {model.id}, 이름: {model.name}")
        return model

    @log_db_operation("CREATE")
    @handle_repository_exceptions
    async def create_oversea(self, db: AsyncSession, model_data: CreateOverseaModel) -> Model:
        """새로운 모델을 생성합니다."""
        model = Model(**model_data.model_dump(), is_foreigner=True)
        self.logger.debug(f"모델 생성 데이터: {model_data.model_dump()}")
        db.add(model)
        await db.commit()
        await db.refresh(model)
        self.logger.info(f"모델 생성 성공 - ID: {model.id}, 이름: {model.name}")
        return model

    @log_db_operation("READ")
    @handle_repository_exceptions
    async def get_domestic_by_id(self, db: AsyncSession, model_id: uuid.UUID) -> Model:
        """ID로 특정 국내 모델을 조회합니다."""
        query = select(Model).where(Model.id == model_id, Model.is_foreigner == False)
        result = await db.execute(query)
        model = result.scalars().first()

        if not model:
            raise EntityNotFoundError("국내 모델", model_id)

        return model

    @log_db_operation("READ")
    @handle_repository_exceptions
    async def get_oversea_by_id(self, db: AsyncSession, model_id: uuid.UUID) -> Model:
        """ID로 특정 해외 모델을 조회합니다."""
        query = select(Model).where(Model.id == model_id, Model.is_foreigner == True)
        result = await db.execute(query)
        model = result.scalars().first()

        if not model:
            raise EntityNotFoundError("해외 모델", model_id)

        return model

    @log_db_operation("READ_ALL")
    @handle_repository_exceptions
    async def get_domestic_models(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Model]:
        """국내 모델 목록을 조회합니다."""
        query = select(Model).where(Model.is_foreigner == False).offset(skip).limit(limit)
        result = await db.execute(query)
        models = result.scalars().all()
        return models

    @log_db_operation("READ_ALL")
    @handle_repository_exceptions
    async def get_oversea_models(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Model]:
        """해외 모델 목록을 조회합니다."""
        query = select(Model).where(Model.is_foreigner == True).offset(skip).limit(limit)
        result = await db.execute(query)
        models = result.scalars().all()
        return models

    @log_db_operation("UPDATE")
    @handle_repository_exceptions
    async def update(self, db: AsyncSession, db_model: Model, update_data: UpdateModel) -> Model:
        """모델 정보를 업데이트합니다."""
        update_dict = update_data.model_dump(exclude_unset=True)
        self.logger.debug(f"모델 업데이트 시작 - ID: {db_model.id}, 업데이트 데이터: {update_dict}")

        for key, value in update_dict.items():
            setattr(db_model, key, value)

        db.add(db_model)
        await db.commit()
        await db.refresh(db_model)

        self.logger.info(f"모델 업데이트 성공 - ID: {db_model.id}, 이름: {db_model.name}")
        return db_model

    @log_db_operation("DELETE")
    @handle_repository_exceptions
    async def delete(self, db: AsyncSession, db_model: Model) -> None:
        """모델을 삭제합니다."""
        model_id = db_model.id
        model_name = db_model.name
        self.logger.debug(f"모델 삭제 시작 - ID: {model_id}, 이름: {model_name}")

        await db.delete(db_model)
        await db.commit()

        self.logger.info(f"모델 삭제 성공 - ID: {model_id}, 이름: {model_name}")

model_repository = ModelRepository()