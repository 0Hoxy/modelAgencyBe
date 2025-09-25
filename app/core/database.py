"""
데이터베이스 연결 및 세션 관리
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# 데이터베이스 엔진 생성 - 실제 DB 연결을 담당하는 핵심 객체
engine = create_async_engine(
    settings.DATABASE_URL,  # PostgreSQL 연결 URL (예: postgresql+asyncpg://user:pass@localhost/db)
    echo=settings.DEBUG,  # True일 때 실행되는 SQL 쿼리를 콘솔에 출력 (개발/디버깅용)
    future=True  # SQLAlchemy 2.0 스타일 사용
)

# 세션 팩토리 생성 - DB 세션을 만들어주는 공장 역할
AsyncSessionLocal = async_sessionmaker(
    engine,  # 위에서 만든 엔진 사용
    class_=AsyncSession,  # 비동기 세션 클래스 사용
    expire_on_commit=False  # 커밋 후에도 객체 상태 유지 (비동기에서 중요)
)


# Base 클래스 - 모든 테이블 모델이 상속받을 기본 클래스
class Base(DeclarativeBase):
    """
    SQLAlchemy ORM 모델의 기본 클래스
    모든 테이블 모델(User, Model 등)이 이 클래스를 상속받아야 함

    예시:
    class User(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
    """
    pass


# 의존성으로 사용할 세션 생성 함수 - FastAPI에서 DB 세션을 주입받을 때 사용
async def get_db():
    """
    FastAPI의 Depends()에서 사용하는 DB 세션 제공 함수

    요청이 올 때마다 새로운 DB 세션을 생성하고,
    요청 처리가 끝나면 자동으로 세션을 닫아서 연결을 정리함

    사용 예시:
    @router.get("/users/")
    async def get_users(db: AsyncSession = Depends(get_db)):
        # 여기서 db를 사용해서 데이터베이스 작업 수행
        return await user_repository.get_all(db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session  # 세션을 반환 (FastAPI가 이를 의존성으로 주입)
        finally:
            await session.close()  # 요청 완료 후 세션 정리
