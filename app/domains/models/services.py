"""
모델(인물) 관련 비즈니스 로직
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import handle_service_exceptions, ValidationError
from app.domains.models.repositories import model_repository
from app.domains.models.schemas import CreateDomesticModel, CreateOverseaModel, UpdateModel, ReadDomesticModel, ReadOverseaModel


class ModelService:
    def __init__(self):
        self.repository = model_repository

    @handle_service_exceptions
    async def create_domestic_model(self, db: AsyncSession, model_data: CreateDomesticModel) -> ReadDomesticModel:
        self._validate_create_model(model_data)
        model = await self.repository.create_domestic(db, model_data)
        return ReadDomesticModel.model_validate(model)

    @handle_service_exceptions
    async def create_oversea_model(self, db: AsyncSession, model_data: CreateOverseaModel) -> ReadOverseaModel:
        self._validate_create_model(model_data)
        model = await self.repository.create_oversea(db, model_data)
        return ReadOverseaModel.model_validate(model)

    @handle_service_exceptions
    async def get_domestic_model_by_id(self, db: AsyncSession, model_id: uuid.UUID) -> ReadDomesticModel:
        model = await self.repository.get_domestic_by_id(db, model_id)
        return ReadDomesticModel.model_validate(model)

    @handle_service_exceptions
    async def get_oversea_model_by_id(self, db: AsyncSession, model_id: uuid.UUID) -> ReadOverseaModel:
        model = await self.repository.get_oversea_by_id(db, model_id)
        return ReadOverseaModel.model_validate(model)

    @handle_service_exceptions
    async def get_domestic_models(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[ReadDomesticModel]:
        if skip < 0:
            raise ValidationError("skip", "0 이상이어야 합니다", skip)
        if limit <= 0 or limit > 100:
            raise ValidationError("limit", "1-100 사이여야 합니다", limit)

        models = await self.repository.get_domestic_models(db, skip, limit)
        return [ReadDomesticModel.model_validate(model) for model in models]

    @handle_service_exceptions
    async def get_oversea_models(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[ReadOverseaModel]:
        if skip < 0:
            raise ValidationError("skip", "0 이상이어야 합니다", skip)
        if limit <= 0 or limit > 100:
            raise ValidationError("limit", "1-100 사이여야 합니다", limit)

        models = await self.repository.get_oversea_models(db, skip, limit)
        return [ReadOverseaModel.model_validate(model) for model in models]

    @handle_service_exceptions
    async def update_domestic_model(self, db: AsyncSession, model_id: uuid.UUID, update_data: UpdateModel) -> ReadDomesticModel:
        existing_model = await self.repository.get_domestic_by_id(db, model_id)
        self._validate_update_model(update_data)
        updated_model = await self.repository.update(db, existing_model, update_data)
        return ReadDomesticModel.model_validate(updated_model)

    @handle_service_exceptions
    async def update_oversea_model(self, db: AsyncSession, model_id: uuid.UUID, update_data: UpdateModel) -> ReadOverseaModel:
        existing_model = await self.repository.get_oversea_by_id(db, model_id)
        self._validate_update_model(update_data)
        updated_model = await self.repository.update(db, existing_model, update_data)
        return ReadOverseaModel.model_validate(updated_model)

    @handle_service_exceptions
    async def delete_domestic_model(self, db: AsyncSession, model_id: uuid.UUID) -> None:
        existing_model = await self.repository.get_domestic_by_id(db, model_id)
        await self.repository.delete(db, existing_model)

    @handle_service_exceptions
    async def delete_oversea_model(self, db: AsyncSession, model_id: uuid.UUID) -> None:
        existing_model = await self.repository.get_oversea_by_id(db, model_id)
        await self.repository.delete(db, existing_model)


    def _validate_create_model(self, model_data: CreateDomesticModel | CreateOverseaModel) -> None:
        if not model_data.name or not model_data.name.strip():
            raise ValidationError("name", "이름은 필수입니다")

        if not model_data.birth_date:
            raise ValidationError("birth_date", "생년월일은 필수입니다.")

        if not model_data.phone:
            raise ValidationError("phone", "연락처는 필수입니다")

        if model_data.height <= 0 or not model_data.height:
            raise ValidationError("height", "키는 0보다 커야 합니다", model_data.height)

    def _validate_update_model(self, update_data: UpdateModel) -> None:
        update_dict = update_data.model_dump(exclude_unset=True)

        if "height" in update_dict and update_dict["height"] <= 0:
            raise ValidationError("height", "키는 0보다 커야 합니다", update_dict["height"])

        if "name" in update_dict and (not update_dict["name"] or not update_dict["name"].strip()):
            raise ValidationError("name", "이름은 비워둘 수 없습니다")

        if "phone" in update_dict and (not update_dict["phone"] or not update_dict["phone"].strip()):
            raise ValidationError("phone", "연락처는 비워둘 수 없습니다")



# 싱글톤 인스턴스
model_service = ModelService()