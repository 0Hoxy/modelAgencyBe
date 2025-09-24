"""
FastAPI Model Agency Backend
메인 애플리케이션 진입점
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.exceptions import ModelAgencyException
from app.domains.models.router import router as models_router

# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="모델 에이전시 백엔드 API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 커스텀 예외 핸들러
@app.exception_handler(ModelAgencyException)
async def model_agency_exception_handler(request: Request, exc: ModelAgencyException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.__class__.__name__,
            "message": exc.message,
            "timestamp": "2024-01-01T00:00:00Z"  # 실제로는 datetime.now()
        }
    )

# API 라우터 등록
app.include_router(models_router, prefix="/api/v1")

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Model Agency Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs" if settings.DEBUG else "disabled"
    }

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
