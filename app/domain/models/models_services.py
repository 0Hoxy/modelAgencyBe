from datetime import date
from typing import List

from app.core.db import db
from app.domain.models.models_repository import models_repository
from app.domain.models.models_schemas import (ReadDomesticModel, ReadGlobalModel, CreateDomesticModel,
                                              CreateGlobalModel, UpdateDomesticModel, ModelResponse, UpdateGlobalModel,
                                              ReadRevisitedModel)


class ModelsServices:
    """모델 서비스 로직"""

    def __init__(self, repository):
        self.repository = repository


    async def get_all_models_of_domestic(self) -> List[ReadDomesticModel]:
        """모든 국내 모델 조회"""
        model_data = await self.repository.get_all_models_of_domestic()

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

    async def get_domestic_model_by_info(self, model_info: ReadRevisitedModel) -> ReadDomesticModel:
        """이름, 전화번호, 생년월일로 국내 모델 조회"""
        result = await self.repository.get_domestic_model_by_info(model_info.name, model_info.phone, model_info.birth)
        if not result:
            raise Exception("등록된 모델이 존재하지 않습니다.")

        return ReadDomesticModel.model_validate(dict(result))

    async def get_foreign_model_by_info(self, name: str, phone: str, birth: date) -> ReadGlobalModel:
        """이름, 전화번호, 생년월일로 해외 모델 조회"""
        model_data = await self.repository.get_foreign_model_by_info(name, phone, birth)
        return ReadGlobalModel.model_validate(model_data)


    async def create_domestic_model(self, create_data: CreateDomesticModel) -> ModelResponse:
        """국내 모델 등록"""
        data_dict = create_data.model_dump()
        data_dict['is_foreigner'] = False

        await self.repository.create_transaction(data_dict)

        return ModelResponse(name=data_dict['name'], message=f"{data_dict['name']} 님의 접수가 성공적으로 완료되었습니다.")

    async def create_foreign_model(self, create_data: CreateGlobalModel) -> ModelResponse:
        """해외 모델 등록"""
        async with db.transaction() as conn:
            data_dict = create_data.model_dump()
            data_dict['is_foreigner'] = True
            model = await self.repository.create_transaction(conn, data_dict)
            if not model:
                raise Exception("해외 모델 등록 실패")

        return ModelResponse(name=data_dict['name'], message=f"{data_dict['name']} 님의 접수가 성공적으로 완료되었습니다.")


    async def update_domestic_model(self, update_data: UpdateDomesticModel) -> ModelResponse:
        """국내 모델 정보 수정"""
        async with db.transaction() as conn:
            data_dict = update_data.model_dump(exclude_none=True, exclude={'id'})

            if not data_dict:
                raise ValueError("수정할 데이터가 없습니다.")

            await self.repository.update_transaction(conn, record_id=update_data.id, data=data_dict)
        return ModelResponse(name=data_dict['name'], message=f"{data_dict['name']} 님의 접수가 성공적으로 완료되었습니다. 재방문을 환영합니다.")

    async def update_foreign_model(self, update_data: UpdateGlobalModel) -> ModelResponse:
        """해외 모델 정보 수정"""
        async with db.transaction() as conn:
            data_dict = update_data.model_dump(exclude_none=True, exclude={'id'})

            if not data_dict:
                raise ValueError("수정할 데이터가 없습니다.")

            await self.repository.update_transaction(conn, record_id=update_data.id, data=data_dict)
        return ModelResponse(name=data_dict['name'], message=f"{data_dict['name']} 님의 접수가 성공적으로 완료되었습니다. 재방문을 환영합니다.")


models_services = ModelsServices(models_repository)