from fastapi import APIRouter

app = APIRouter(
    prefix="/mails",
    tags=["mails"],
    responses={404: {"description": "Not found"}},
)

@app.get("/tempPassword")
async def send_temp_password():
 return {}