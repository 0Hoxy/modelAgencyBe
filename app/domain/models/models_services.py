from datetime import date
from typing import List, Optional

from fastapi import HTTPException

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
        try:
            model_data = await self.repository.get_all_models_of_domestic()
            
            if not model_data:
                return []
            
            return [
                ReadDomesticModel.model_validate(dict(record))
                for record in model_data
            ]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"국내 모델 목록 조회 중 오류가 발생했습니다: {str(e)}"
            )

    async def get_all_models_of_foreign(self) -> List[ReadGlobalModel]:
        """모든 해외 모델 조회"""
        try:
            model_data = await self.repository.get_all_models_of_foreign()
            
            if not model_data:
                return []
            
            return [
                ReadGlobalModel.model_validate(dict(record))
                for record in model_data
            ]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"해외 모델 목록 조회 중 오류가 발생했습니다: {str(e)}"
            )

    async def get_domestic_model_by_info(self, model_info: ReadRevisitedModel) -> ReadDomesticModel:
        """이름, 전화번호, 생년월일로 국내 모델 조회"""
        try:
            result = await self.repository.get_domestic_model_by_info(
                model_info.name, 
                model_info.phone, 
                model_info.birth
            )
            
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail="등록된 모델이 존재하지 않습니다."
                )
            
            return ReadDomesticModel.model_validate(dict(result))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"국내 모델 조회 중 오류가 발생했습니다: {str(e)}"
            )

    async def get_foreign_model_by_info(self, model_info: ReadRevisitedModel) -> ReadGlobalModel:
        """이름, 전화번호, 생년월일로 해외 모델 조회"""
        try:
            result = await self.repository.get_foreign_model_by_info(
                model_info.name,
                model_info.phone,
                model_info.birth
            )
            
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail="등록된 모델이 존재하지 않습니다."
                )
            
            return ReadGlobalModel.model_validate(dict(result))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"해외 모델 조회 중 오류가 발생했습니다: {str(e)}"
            )


    async def create_domestic_model(self, create_data: CreateDomesticModel) -> ModelResponse:
        """국내 모델 등록"""
        try:
            async with db.transaction() as conn:
                data_dict = create_data.model_dump()
                data_dict['is_foreigner'] = False
                
                await self.repository.create_transaction(conn, data_dict)
                
                return ModelResponse(
                    name=data_dict['name'], 
                    message=f"{data_dict['name']} 님의 접수가 성공적으로 완료되었습니다."
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"국내 모델 등록 중 오류가 발생했습니다: {str(e)}"
            )

    async def create_foreign_model(self, create_data: CreateGlobalModel) -> ModelResponse:
        """해외 모델 등록"""
        try:
            async with db.transaction() as conn:
                data_dict = create_data.model_dump()
                data_dict['is_foreigner'] = True
                
                await self.repository.create_transaction(conn, data_dict)
                
                return ModelResponse(
                    name=data_dict['name'], 
                    message=f"{data_dict['name']} 님의 접수가 성공적으로 완료되었습니다."
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"해외 모델 등록 중 오류가 발생했습니다: {str(e)}"
            )


    async def update_domestic_model(self, update_data: UpdateDomesticModel) -> ModelResponse:
        """국내 모델 정보 수정"""
        try:
            data_dict = update_data.model_dump(exclude_none=True, exclude={'id'})

            if not data_dict:
                raise HTTPException(
                    status_code=400,
                    detail="수정할 데이터가 없습니다."
                )

            async with db.transaction() as conn:
                await self.repository.update_transaction(conn, record_id=update_data.id, data=data_dict)
            
            return ModelResponse(
                name=data_dict.get('name', '모델'),
                message=f"{data_dict.get('name', '모델')} 님의 정보가 성공적으로 수정되었습니다. 재방문을 환영합니다."
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"국내 모델 정보 수정 중 오류가 발생했습니다: {str(e)}"
            )

    async def update_foreign_model(self, update_data: UpdateGlobalModel) -> ModelResponse:
        """해외 모델 정보 수정"""
        try:
            data_dict = update_data.model_dump(exclude_none=True, exclude={'id'})

            if not data_dict:
                raise HTTPException(
                    status_code=400,
                    detail="수정할 데이터가 없습니다."
                )

            async with db.transaction() as conn:
                await self.repository.update_transaction(conn, record_id=update_data.id, data=data_dict)
            
            return ModelResponse(
                name=data_dict.get('name', '모델'),
                message=f"{data_dict.get('name', '모델')} 님의 정보가 성공적으로 수정되었습니다. 재방문을 환영합니다."
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"해외 모델 정보 수정 중 오류가 발생했습니다: {str(e)}"
            )


models_services = ModelsServices(models_repository)