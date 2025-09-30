from fastapi import APIRouter

from app.core.db import Database
from app.domain.models.models_services import models_services

app = APIRouter(
    prefix="/models",
    tags=["models"],
    responses={404: {"description": "Not found"}},
)

@app.get("/domestic")
async def read_domestic():
    return await models_services.get_all_models_of_domestic()


@app.get("/global")
async def read_global():
    return await models_services.get_all_models_of_foreign()

@app.get("{id}/physical")
async def read_physical_size():
    return await models_services.get_models_physical_size()