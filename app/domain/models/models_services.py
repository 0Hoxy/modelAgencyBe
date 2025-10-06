from datetime import date, datetime
from typing import List, Optional

from fastapi import HTTPException

from app.core.db import db
from app.shared.validators import serialize_phone
from app.domain.models.models_repository import models_repository
from app.domain.models.models_schemas import (ReadDomesticModel, ReadGlobalModel, CreateDomesticModel,
                                              CreateGlobalModel, UpdateDomesticModel, ModelResponse, UpdateGlobalModel,
                                              ReadRevisitedModel)
from app.domain.admins.admins_repository import admins_repository


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
            # PhoneNumber 객체를 E.164 문자열로 변환
            phone_str = serialize_phone(model_info.phone, "E164")
            
            result = await self.repository.get_domestic_model_by_info(
                model_info.name, 
                phone_str, 
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
            # PhoneNumber 객체를 E.164 문자열로 변환
            phone_str = serialize_phone(model_info.phone, "E164")
            
            result = await self.repository.get_foreign_model_by_info(
                model_info.name,
                phone_str,
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
                # exclude_unset: 프론트엔드에서 보내지 않은 필드 제외
                # exclude_none: None 값 제외 (DB 기본값 사용)
                data_dict = create_data.model_dump(
                    exclude_unset=True,
                    exclude_none=True, 
                    exclude={'id', 'is_foreigner', 'created_at', 'updated_at'}
                )
                data_dict['is_foreigner'] = False
                # 전화번호를 E.164 형식으로 일관 저장
                if 'phone' in data_dict and create_data.phone is not None:
                    data_dict['phone'] = serialize_phone(create_data.phone, "E164")
                if 'agency_manager_phone' in data_dict and create_data.agency_manager_phone is not None:
                    data_dict['agency_manager_phone'] = serialize_phone(create_data.agency_manager_phone, "E164")
                
                # 1) 모델 생성
                created = await self.repository.create_transaction(conn, data_dict)
                # 2) 카메라 테스트 초기 레코드 생성 (동일 트랜잭션)
                if created and created.get('id'):
                    await admins_repository.create_camera_test_transaction(
                        conn=conn,
                        model_id=created['id'],
                        visited_at=datetime.now()
                    )
                
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
                # exclude_unset: 프론트엔드에서 보내지 않은 필드 제외
                # exclude_none: None 값 제외 (DB 기본값 사용)
                data_dict = create_data.model_dump(
                    exclude_unset=True,
                    exclude_none=True, 
                    exclude={'id', 'is_foreigner', 'created_at', 'updated_at'}
                )
                data_dict['is_foreigner'] = True
                # 전화번호를 E.164 형식으로 일관 저장
                if 'phone' in data_dict and create_data.phone is not None:
                    data_dict['phone'] = serialize_phone(create_data.phone, "E164")
                
                # 1) 모델 생성
                created = await self.repository.create_transaction(conn, data_dict)
                # 2) 카메라 테스트 초기 레코드 생성 (동일 트랜잭션)
                if created and created.get('id'):
                    await admins_repository.create_camera_test_transaction(
                        conn=conn,
                        model_id=created['id'],
                        visited_at=datetime.now()
                    )
                
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
            # 전화번호를 E.164 형식으로 일관 저장
            if 'phone' in data_dict and update_data.phone is not None:
                data_dict['phone'] = serialize_phone(update_data.phone, "E164")
            if 'agency_manager_phone' in data_dict and update_data.agency_manager_phone is not None:
                data_dict['agency_manager_phone'] = serialize_phone(update_data.agency_manager_phone, "E164")

            if not data_dict:
                raise HTTPException(
                    status_code=400,
                    detail="수정할 데이터가 없습니다."
                )

            async with db.transaction() as conn:
                await self.repository.update_transaction(conn, record_id=update_data.id, data=data_dict)
                # 방문 기록 남기기 (동일 트랜잭션): PENDING 상태의 cameratest 추가
                await admins_repository.create_camera_test_transaction(
                    conn=conn,
                    model_id=update_data.id,
                    visited_at=datetime.now()
                )
            
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
            # 전화번호를 E.164 형식으로 일관 저장
            if 'phone' in data_dict and update_data.phone is not None:
                data_dict['phone'] = serialize_phone(update_data.phone, "E164")

            if not data_dict:
                raise HTTPException(
                    status_code=400,
                    detail="수정할 데이터가 없습니다."
                )

            async with db.transaction() as conn:
                await self.repository.update_transaction(conn, record_id=update_data.id, data=data_dict)
                # 방문 기록 남기기 (동일 트랜잭션): PENDING 상태의 cameratest 추가
                await admins_repository.create_camera_test_transaction(
                    conn=conn,
                    model_id=update_data.id,
                    visited_at=datetime.now()
                )
            
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