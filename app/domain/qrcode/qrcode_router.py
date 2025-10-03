from fastapi import APIRouter

app = APIRouter(
    prefix="/qrcode",
    tags=["qrcode"],
    responses={404: {"description": "Not found"}},
)

@app.get("generate")
async def generate_qrcode():
    return {}