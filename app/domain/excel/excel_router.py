from fastapi import APIRouter

app = APIRouter(
    prefix="/excel",
    tags=["excel"],
    responses={404: {"description": "Not found"}},
)

@app.get("/domestic")
async def get_domestic_models_excel():
    """국내 모델 리스트 엑셀 다운로드"""
    return {}

@app.get("/global/")
async def get_global_models_excel():
    """해외 모델 리스트 엑셀 다운로드"""
    return {}