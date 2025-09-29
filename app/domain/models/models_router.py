from fastapi import APIRouter

from app.core.db import Database
app = APIRouter(
    prefix="/models",
    tags=["models"],
    responses={404: {"description": "Not found"}},
)

@app.get("/domestic")
async def read_domestic():

    return {}

@app.get("/global")
async def read_global():
    return {}

