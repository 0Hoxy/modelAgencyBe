from fastapi import APIRouter

from app.domain.models.models_services import models_services

app = APIRouter(
    prefix="/admins",
    tags=["admins"],
    responses={404: {"description": "Not found"}},
)

@app.get("/models/domestic")
async def read_domestic_model():
    """국내 모델 리스트 조회 (검색 조건 포함)"""
    return {}

@app.get("/models/global")
async def read_global_model():
    """헤외 모델 리스트 조회 (검색 조건 포함)"""
    return {}

@app.post("/models/global")
async def create_foreign_model():
    """국내 모델 등록 (관리자)"""
    return {}

@app.post("/models/domestic")
async def create_foreign_model():
    """해외 모델 등록 (관리자)"""
    return {}

@app.put("/models/domestic")
async def update_domestic_model(model_id):
    """국내 모델 정보 수정"""
    return {}

@app.put("/models/global")
async def update_global_model(model_id):
    """해외 모델 정보 수정"""
    return {}

@app.get("{id}/physical")
async def read_physical_size():
    """모델 신체 사이즈 조회"""
    return await models_services.get_models_physical_size()

@app.delete("/models/{model_id}")
async def delete_model(model_id):
    return {}

@app.post("cameraTest/{model_id}")
async def toggle_camera_test_status(model_id):
    """카메라 테스트 상태 변경"""
    return {}

@app.post("/models/cameraTest/{model_id}")
async def create_camera_test_status(model_id):
    """기존 등록 모델 카메라 테스트 등록"""
    return {}

@app.get("/dashboard")
async def read_dashboard():
    """대시보드 정보 조회"""
    return {}