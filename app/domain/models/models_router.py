from fastapi import APIRouter

from app.domain.models.models_schemas import (
    ReadRevisitedModel,
    CreateDomesticModel,
    CreateGlobalModel,
    UpdateDomesticModel,
    UpdateGlobalModel,
)
from app.domain.models.models_services import models_services

app = APIRouter(
    prefix="/models",
    tags=["models"],
    responses={404: {"description": "Not found"}},
)

@app.post("/domestic/revisit-verification")
async def verify_domestic_revisit(request: ReadRevisitedModel):
    """국내 모델 재방문 확인"""
    return await models_services.get_domestic_model_by_info(request)

@app.post("/global/revisit-verification")
async def verify_global_revisit(request: ReadRevisitedModel):
    """해외 모델 재방문 확인"""
    return await models_services.get_foreign_model_by_info(request)

@app.get("/domestic")
async def read_domestic():
    """국내 모델 목록 조회"""
    return await models_services.get_all_models_of_domestic()

@app.get("/global")
async def read_global():
    """해외 모델 목록 조회"""
    return await models_services.get_all_models_of_foreign()

@app.post("/domestic")
async def create_domestic(request: CreateDomesticModel):
    """국내 모델 등록"""
    return await models_services.create_domestic_model(request)

@app.post("/global")
async def create_global(request: CreateGlobalModel):
    """해외 모델 등록"""
    return await models_services.create_foreign_model(request)

@app.put("/domestic")
async def update_domestic(request: UpdateDomesticModel):
    """국내 모델 정보 수정"""
    return await models_services.update_domestic_model(request)

@app.put("/global")
async def update_global(request: UpdateGlobalModel):
    """해외 모델 정보 수정"""
    return await models_services.update_foreign_model(request)