from datetime import date
from typing import List

from app.domain.models.models_repository import models_repository
from app.domain.models.models_schemas import (ReadDomesticModel, ReadGlobalModel, CreateDomesticModel,
                            CreateGlobalModel, UpdateDomesticModel, ModelResponse, UpdateGlobalModel)


class ModelsServices:
    """모델 서비스 로직"""

    def __init__(self, repository):
        self.repository = repository


    async def get_all_models_of_domestic(self) -> List[ReadDomesticModel]:
        """모든 국내 모델 조회"""
        model_data = await self.repository.get_all_models_of_foreign()

        return [
            ReadDomesticModel.model_validate(dict(record))
            for record in model_data
        ]

    async def get_all_models_of_foreign(self) -> List[ReadGlobalModel]:
        """모든 해외 모델 조회"""
        model_data = await self.repository.get_all_models_of_foreign()

        return [
            ReadGlobalModel.model_validate(dict(record))
            for record in model_data
        ]

    async def get_domestic_model_by_info(self, name: str, phone: str, birth: date) -> ReadDomesticModel:
        """이름, 전화번호, 생년월일로 국내 모델 조회"""
        model_data = await self.repository.get_domestic_model_by_info(name, phone, birth)
        return ReadDomesticModel.model_validate(model_data)

    async def get_foreign_model_by_info(self, name: str, phone: str, birth: date) -> ReadGlobalModel:
        """이름, 전화번호, 생년월일로 해외 모델 조회"""
        model_data = await self.repository.get_foreign_model_by_info(name, phone, birth)
        return ReadGlobalModel.model_validate(model_data)


    async def create_domestic_model(self, create_data: CreateDomesticModel) -> ModelResponse:
        """국내 모델 등록"""
        data_dict = create_data.model_dump()
        data_dict['is_foreigner'] = False

        await self.repository.create(data_dict)

        return ModelResponse(name=data_dict['name'], message=f"{data_dict['name']} 님의 접수가 성공적으로 완료되었습니다.")

    async def create_foreign_model(self, create_data: CreateGlobalModel) -> ModelResponse:
        """해외 모델 등록"""
        data_dict = create_data.model_dump()
        data_dict['is_foreigner'] = True
        await self.repository.create(data_dict)

        return ModelResponse(name=data_dict['name'], message=f"{data_dict['name']} 님의 접수가 성공적으로 완료되었습니다.")


    async def update_domestic_model(self, update_data: UpdateDomesticModel) -> ModelResponse:
        data_dict = update_data.model_dump(exclude_none=True, exclude={'id'})

        if not data_dict:
            raise ValueError("수정할 데이터가 없습니다.")

        await self.repository.update(record_id=update_data.id, data=data_dict)
        return ModelResponse(name=data_dict['name'], message=f"{data_dict['name']} 님의 접수가 성공적으로 완료되었습니다. 재방문을 환영합니다.")

    async def update_foreign_model(self, update_data: UpdateGlobalModel) -> ModelResponse:
        data_dict = update_data.model_dump(exclude_none=True, exclude={'id'})

        if not data_dict:
            raise ValueError("수정할 데이터가 없습니다.")

        await self.repository.update(record_id=update_data.id, data=data_dict)
        return ModelResponse(name=data_dict['name'], message=f"{data_dict['name']} 님의 접수가 성공적으로 완료되었습니다. 재방문을 환영합니다.")


models_services = ModelsServices(models_repository)