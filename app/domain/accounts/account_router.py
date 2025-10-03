from uuid import UUID

from fastapi import APIRouter

app = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    responses={404: {"description": "Not found"}},
)

@app.post("/signup/admins")
async def create_account():
    """관리자 계정 생성"""
    return {}

@app.post("/signup/directors")
async def create_director():
    """감독 계정 생성"""
    return {}

@app.post("/password/admins")
async def change_admins_password():
    """관리자 계정 비밀번호 변경"""
    return {}

@app.post("/password/directors")
async def change_directors_password():
    """감독 계정 비밀번호 변경"""
    return {}

@app.delete("/directors/{admin_id}")
async def withdraw_director(admin_id: UUID):
    """감독 계정 삭제"""
    return {}

@app.post("/login")
async def login():
    """로그인"""
    return {}