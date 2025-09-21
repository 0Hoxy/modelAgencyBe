"""
API v1 메인 라우터
모든 하위 라우터들을 통합하는 메인 라우터
"""

from fastapi import APIRouter
from app.api.v1.auth.router import auth_router
from app.api.v1.models.router import models_router
from app.api.v1.bookings.router import bookings_router

# 메인 API 라우터 생성
api_router = APIRouter()

# 하위 라우터들 등록
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["인증"]
)

api_router.include_router(
    models_router,
    prefix="/models",
    tags=["모델 관리"]
)

api_router.include_router(
    bookings_router,
    prefix="/bookings",
    tags=["예약 관리"]
)

# 추가 도메인별 라우터들을 여기에 등록
# 예: users, agencies, payments, notifications 등
