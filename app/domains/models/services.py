"""
모델(인물) 관련 비즈니스 로직
"""
import uuid
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_service_logger, log_service_operation
from app.core.exceptions import handle_service_exceptions, ValidationError, EntityNotFoundError
from app.domains.models.repositories import model_repository
from app.domains.models.schemas import CreateDomesticModel, CreateOverseaModel, UpdateModel, ReadDomesticModel, ReadOverseaModel, CreateModelResponse
from app.domains.models.models import Model


class ModelService:
    def __init__(self):
        """Service 초기화"""
        self.logger = get_service_logger("model")
        self.repository = model_repository

    @log_service_operation("CREATE")
    @handle_service_exceptions
    async def create_model(self, db: AsyncSession, model_data: CreateDomesticModel | CreateOverseaModel) -> ReadDomesticModel | ReadOverseaModel:
        """새로운 모델을 생성합니다."""
        self.logger.debug(f"모델 생성 요청 - 데이터: {model_data.model_dump()}")

        # 비즈니스 로직 검증
        await self._validate_create_model(db, model_data)

        # Repository를 통해 모델 생성
        model = await self.repository.create(db, model_data)

        self.logger.info(f"모델 생성 완료 - ID: {model.id}, 이름: {model.name}")

        # 모델 타입에 따라 적절한 스키마 선택
        if isinstance(model_data, CreateDomesticModel):
            return ReadDomesticModel.model_validate(model)
        else:
            return ReadOverseaModel.model_validate(model)

    @log_service_operation("READ")
    @handle_service_exceptions
    async def get_model_by_id(self, db: AsyncSession, model_id: uuid.UUID) -> ReadDomesticModel | ReadOverseaModel:
        """ID로 모델을 조회합니다."""
        self.logger.debug(f"모델 조회 요청 - ID: {model_id}")

        model = await self.repository.get_by_id(db, model_id)

        self.logger.debug(f"모델 조회 완룈 - ID: {model_id}, 이름: {model.name}")

        # 모델 속성에 따라 적절한 스키마 선택
        if hasattr(model, 'has_agency') and model.has_agency is not None:
            return ReadDomesticModel.model_validate(model)
        else:
            return ReadOverseaModel.model_validate(model)

    @log_service_operation("READ_ALL")
    @handle_service_exceptions
    async def get_models(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[ReadDomesticModel | ReadOverseaModel]:
        """모델 목록을 조회합니다."""
        self.logger.debug(f"모델 목록 조회 요청 - skip: {skip}, limit: {limit}")

        # 페이징 검증
        if skip < 0:
            raise ValidationError("skip", "0 이상이어야 합니다", skip)
        if limit <= 0 or limit > 100:
            raise ValidationError("limit", "1-100 사이여야 합니다", limit)

        models = await self.repository.get_all(db, skip, limit)

        self.logger.info(f"모델 목록 조회 완료 - 조회된 개수: {len(models)}")

        result = []
        for model in models:
            if hasattr(model, 'has_agency') and model.has_agency is not None:
                result.append(ReadDomesticModel.model_validate(model))
            else:
                result.append(ReadOverseaModel.model_validate(model))
        return result

    @log_service_operation("UPDATE")
    @handle_service_exceptions
    async def update_model(self, db: AsyncSession, model_id: uuid.UUID, update_data: UpdateModel) -> ReadDomesticModel | ReadOverseaModel:
        """모델 정보를 업데이트합니다."""
        self.logger.debug(f"모델 업데이트 요청 - ID: {model_id}, 데이터: {update_data.model_dump(exclude_unset=True)}")

        # 모델 존재 확인
        existing_model = await self.repository.get_by_id(db, model_id)

        # 비즈니스 로직 검증
        await self._validate_update_model(db, model_id, update_data)

        # Repository를 통해 모델 업데이트
        updated_model = await self.repository.update(db, existing_model, update_data)

        self.logger.info(f"모델 업데이트 완료 - ID: {model_id}, 이름: {updated_model.name}")

        # 모델 속성에 따라 적절한 스키마 선택
        if hasattr(updated_model, 'has_agency') and updated_model.has_agency is not None:
            return ReadDomesticModel.model_validate(updated_model)
        else:
            return ReadOverseaModel.model_validate(updated_model)

    @log_service_operation("DELETE")
    @handle_service_exceptions
    async def delete_model(self, db: AsyncSession, model_id: uuid.UUID) -> None:
        """모델을 삭제합니다."""
        self.logger.debug(f"모델 삭제 요청 - ID: {model_id}")

        # 모델 존재 확인
        existing_model = await self.repository.get_by_id(db, model_id)

        # 비즈니스 로직 검증 (삭제 전 검증)
        await self._validate_delete_model(db, existing_model)

        # Repository를 통해 모델 삭제
        await self.repository.delete(db, existing_model)

        self.logger.info(f"모델 삭제 완료 - ID: {model_id}, 이름: {existing_model.name}")


# --- 검증 ---
    async def _validate_create_model(self, db: AsyncSession, model_data: CreateDomesticModel | CreateOverseaModel) -> None:
        """모델 생성 시 비즈니스 로직 검증"""

        # 필수 필드 검증
        if not model_data.name or not model_data.name.strip():
            raise ValidationError("name", "이름은 필수입니다")

        if not model_data.phone:
            raise ValidationError("phone", "연락처는 필수입니다")

        if model_data.height <= 0:
            raise ValidationError("height", "키는 0보다 커야 합니다", model_data.height)

        # 연락처 중복 검증 (추후 구현 가능)
        # existing_models = await self.repository.get_by_phone(db, model_data.phone)
        # if existing_models:
        #     raise ValidationError("phone", "이미 등록된 연락처입니다", model_data.phone)

    async def _validate_update_model(self, db: AsyncSession, model_id: uuid.UUID, update_data: UpdateModel) -> None:
        """모델 업데이트 시 비즈니스 로직 검증"""

        update_dict = update_data.model_dump(exclude_unset=True)

        # 높이 검증
        if "height" in update_dict and update_dict["height"] <= 0:
            raise ValidationError("height", "키는 0보다 커야 합니다", update_dict["height"])

        # 이름 검증
        if "name" in update_dict and (not update_dict["name"] or not update_dict["name"].strip()):
            raise ValidationError("name", "이름은 비워둘 수 없습니다")

        # 연락처 검증
        if "phone" in update_dict and (not update_dict["phone"] or not update_dict["phone"].strip()):
            raise ValidationError("phone", "연락처는 비워둘 수 없습니다")

    async def _validate_delete_model(self, db: AsyncSession, model: Model) -> None:
        """모델 삭제 시 비즈니스 로직 검증"""

        # 삭제 가능 여부 검증 (예: 진행 중인 프로젝트가 있는지 확인)
        # 현재는 기본적인 검증만 수행
        pass


# 싱글톤 인스턴스
model_service = ModelService()