from fastapi import APIRouter

from app.core.db import Database
from app.domain.models.models_schemas import ReadRevisitedModel
from app.domain.models.models_services import models_services

app = APIRouter(
    prefix="/models",
    tags=["models"],
    responses={404: {"description": "Not found"}},
)

@app.get("/revisit-info")
async def get_revisit_info():
    return {}

@app.post("/domestic/revisit-verification")
async def get_revisit_verification(request: ReadRevisitedModel):
    result = await models_services.get_domestic_model_by_info(request)
    return result

@app.post("/global/revisit-verification")
async def get_revisit_verification():
    return {}

@app.get("/domestic")
async def read_domestic():
    return await models_services.get_all_models_of_domestic()

@app.get("/global")
async def read_global():
    return await models_services.get_all_models_of_foreign()

@app.post("/domestic")
async def create_domestic():
    return {}

@app.post("/global")
async def create_global():
    return {}

@app.put("/domestic/{model_id}")
async def update_domestic(model_id: int):
    return {}

@app.put("/global/{model_id}")
async def update_global(model_id: int):
    return {}