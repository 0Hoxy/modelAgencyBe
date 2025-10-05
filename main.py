from contextlib import asynccontextmanager

from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

from app.core.db import db
from app.core.config import settings
from app.domain.admins import admins_router
from app.domain.excel import excel_router
from app.domain.models import models_router
from app.domain.models.models_schemas import ReadRevisitedModel
from app.domain.models.models_services import models_services
from app.domain.smtp import smtp_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시 실행
    try:
        await db.connect()
        print("데이터베이스 연결 성공")
    except Exception as e:
        print(f"데이터베이스 연결 실패: {e}")

    yield  # 애플리케이션 실행

    # 종료 시 실행
    await db.disconnect()
    print("데이터베이스 연결 해제 완료")

app = FastAPI(
    title="모델 에이전시 API",
    version="1.0.0",
    description="모델 에이전시 백엔드 API",
    lifespan=lifespan)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),  # .env에서 설정한 허용 도메인 목록
    allow_credentials=True,  # 쿠키 등 인증 정보 포함 허용
    allow_methods=["*"],  # 모든 HTTP 메소드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],  # 모든 헤더 허용
)

app.include_router(models_router.app)
app.include_router(admins_router.app)
app.include_router(smtp_router.app)
app.include_router(excel_router.app)

@app.get("/")
async def root():
    """루트 엔드포인트"""
    try:
        return {
            "message": "모델 에이전시 백엔드 API",
            "version": "1.0.0",
            "status": "실행중"
        }
    except Exception as e:
        return {
            "message": "모델 에이전시 백엔드 API",
            "version": "1.0.0",
            "status": "종료 상태",
            "error": e
        }

@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)