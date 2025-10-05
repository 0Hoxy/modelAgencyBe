"""
SMTP 관련 라우터
- 임시 비밀번호 발송
"""
from fastapi import APIRouter

from app.domain.smtp.smtp_service import smtp_service
from app.domain.smtp.smtp_schemas import TempPasswordRequest, TempPasswordResponse


app = APIRouter(
    prefix="/mails",
    tags=["mails"],
    responses={404: {"description": "Not found"}},
)


@app.post("/tempPassword", response_model=TempPasswordResponse)
async def send_temp_password(request: TempPasswordRequest):
    """
    임시 비밀번호 발송
    
    - 입력된 이메일(pid)로 계정을 찾음
    - 임시 비밀번호를 생성하여 DB에 저장
    - 생성된 임시 비밀번호를 이메일로 전송
    """
    return await smtp_service.send_temp_password(request)