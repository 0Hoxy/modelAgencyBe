# Model Agency Backend

FastAPI를 사용한 모델 에이전시 백엔드 API 서버입니다.

## 프로젝트 구조

```
modelAgencyBe/
├── app/
│   ├── main.py                 # FastAPI 앱 진입점
│   ├── config/                 # 설정 관리
│   │   ├── settings.py         # 환경 설정
│   │   └── database.py         # DB 연결 설정
│   ├── core/                   # 핵심 기능
│   │   ├── dependencies.py     # 의존성 주입
│   │   ├── exceptions.py       # 커스텀 예외
│   │   └── middleware.py       # 미들웨어
│   ├── api/                    # API 라우터
│   │   └── v1/
│   │       ├── router.py       # 메인 라우터
│   │       ├── auth/           # 인증 API
│   │       ├── models/         # 모델 관리 API
│   │       └── bookings/       # 예약 관리 API
│   ├── service/                # 비즈니스 로직
│   ├── repository/             # 데이터 접근 계층
│   ├── models/                 # ORM 모델
│   ├── schemas/                # Pydantic 스키마
│   └── utils/                  # 유틸리티
├── tests/                      # 테스트 코드
├── requirements.txt            # 의존성 패키지
└── README.md                   # 프로젝트 문서
```

## 📁 폴더 및 파일별 상세 설명

### 🚀 **app/main.py** - FastAPI 앱 진입점

**역할**: 애플리케이션의 메인 진입점, FastAPI 앱 생성 및 설정

**작성해야 할 코드**:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import get_settings
from app.api.v1.router import api_router

# FastAPI 앱 생성
app = FastAPI(title="Model Agency API")

# 미들웨어 설정
app.add_middleware(CORSMiddleware, ...)

# 라우터 등록
app.include_router(api_router, prefix="/api/v1")

# 루트 엔드포인트
@app.get("/")
async def root():
    return {"message": "Model Agency API"}
```

### ⚙️ **app/config/** - 설정 관리

**역할**: 환경 변수, 데이터베이스 연결 등 애플리케이션 설정 관리

#### **app/config/settings.py** - 환경 설정

**역할**: Pydantic을 사용한 타입 안전한 설정 관리

**작성해야 할 코드**:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "ModelAgencyBe"
    DEBUG: bool = True
    DATABASE_URL: str
    SECRET_KEY: str
    # ... 기타 설정들

    class Config:
        env_file = ".env"
```

#### **app/config/database.py** - DB 연결 설정

**역할**: 데이터베이스 연결 및 세션 관리

**작성해야 할 코드**:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 데이터베이스 엔진 생성
engine = create_async_engine(DATABASE_URL)

# 세션 팩토리 생성
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)

# 의존성으로 사용할 세션 생성 함수
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

### 🔧 **app/core/** - 핵심 기능

**역할**: 애플리케이션 전반에서 사용되는 공통 기능들

#### **app/core/dependencies.py** - 의존성 주입

**역할**: FastAPI의 Depends를 활용한 의존성 관리

**작성해야 할 코드**:

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

def get_current_user(credentials = Depends(security)):
    # JWT 토큰 검증 로직
    return user_info

def get_admin_user(current_user = Depends(get_current_user)):
    # 관리자 권한 검증 로직
    return admin_user
```

#### **app/core/exceptions.py** - 커스텀 예외

**역할**: 비즈니스 로직에 맞는 커스텀 예외 클래스 정의

**작성해야 할 코드**:

```python
from fastapi import HTTPException, status

class ModelAgencyException(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code

class UserNotFoundException(ModelAgencyException):
    def __init__(self, user_id: str):
        super().__init__(f"사용자를 찾을 수 없습니다: {user_id}", 404)
```

#### **app/core/middleware.py** - 미들웨어

**역할**: 요청/응답 처리 전후에 실행되는 미들웨어

**작성해야 할 코드**:

```python
from fastapi import Request
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### 🌐 **app/api/** - API 라우터

**역할**: HTTP 요청을 처리하고 응답을 반환하는 API 엔드포인트 정의

#### **app/api/v1/router.py** - 메인 라우터

**역할**: 모든 하위 라우터들을 통합하는 메인 라우터

**작성해야 할 코드**:

```python
from fastapi import APIRouter
from app.api.v1.auth.router import auth_router
from app.api.v1.models.router import models_router

api_router = APIRouter()

# 하위 라우터들 등록
api_router.include_router(auth_router, prefix="/auth", tags=["인증"])
api_router.include_router(models_router, prefix="/models", tags=["모델"])
```

#### **app/api/v1/{domain}/router.py** - 도메인별 라우터

**역할**: 특정 도메인의 API 엔드포인트 정의

**작성해야 할 코드**:

```python
from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_user
from app.schemas.model import ModelCreate, ModelResponse

router = APIRouter()

@router.post("/", response_model=ModelResponse)
async def create_model(
    model_data: ModelCreate,
    current_user = Depends(get_current_user)
):
    # 비즈니스 로직 호출
    return await model_service.create_model(model_data, current_user)
```

#### **app/api/v1/{domain}/schemas.py** - 요청/응답 스키마

**역할**: API 요청/응답 데이터의 검증 및 직렬화

**작성해야 할 코드**:

```python
from pydantic import BaseModel, Field
from typing import Optional

class ModelCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=10)
    price_per_hour: int = Field(..., gt=0)

class ModelResponse(BaseModel):
    model_id: str
    name: str
    description: str
    price_per_hour: int
    created_at: datetime
```

### 🏢 **app/service/** - 비즈니스 로직 계층

**역할**: 비즈니스 로직 처리, 트랜잭션 관리, 도메인 규칙 적용

**작성해야 할 코드**:

```python
from app.repository.model_repository import ModelRepository
from app.core.exceptions import ModelNotFoundException

class ModelService:
    def __init__(self, model_repo: ModelRepository):
        self.model_repo = model_repo

    async def create_model(self, model_data: ModelCreate, user_id: str):
        # 비즈니스 로직 검증
        if model_data.price_per_hour < 10000:
            raise ValidationException("최소 가격은 10,000원입니다")

        # 리포지토리를 통한 데이터 저장
        return await self.model_repo.create(model_data)

    async def get_model_by_id(self, model_id: str):
        model = await self.model_repo.get_by_id(model_id)
        if not model:
            raise ModelNotFoundException(model_id)
        return model
```

### 🗄️ **app/repository/** - 데이터 접근 계층

**역할**: 데이터베이스와의 상호작용, CRUD 작업 수행

#### **app/repository/base.py** - 기본 리포지토리

**역할**: 공통 CRUD 작업을 정의하는 추상 클래스

**작성해야 할 코드**:

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Generic, TypeVar

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    async def create(self, obj_in: T) -> T:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 10) -> List[T]:
        pass
```

#### **app/repository/{domain}\_repository.py** - 도메인별 리포지토리

**역할**: 특정 도메인의 데이터 접근 로직 구현

**작성해야 할 코드**:

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.model import Model
from app.schemas.model import ModelCreate

class ModelRepository(BaseRepository[Model, str]):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, model_data: ModelCreate) -> Model:
        db_model = Model(**model_data.dict())
        self.db.add(db_model)
        await self.db.commit()
        await self.db.refresh(db_model)
        return db_model

    async def get_by_id(self, model_id: str) -> Optional[Model]:
        result = await self.db.execute(
            select(Model).where(Model.id == model_id)
        )
        return result.scalar_one_or_none()
```

### 📊 **app/models/** - ORM 모델

**역할**: 데이터베이스 테이블과 매핑되는 SQLAlchemy 모델 정의

**작성해야 할 코드**:

```python
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Model(Base):
    __tablename__ = "models"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=False)
    price_per_hour = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### 📋 **app/schemas/** - Pydantic 스키마

**역할**: API 요청/응답 데이터 검증 및 직렬화

#### **app/schemas/base.py** - 기본 스키마

**역할**: 공통으로 사용되는 기본 스키마 정의

**작성해야 할 코드**:

```python
from pydantic import BaseModel
from datetime import datetime

class BaseResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = datetime.now()

class PaginatedResponse(BaseModel):
    total: int
    skip: int
    limit: int
    has_next: bool
    has_prev: bool
```

#### **app/schemas/{domain}.py** - 도메인별 스키마

**역할**: 특정 도메인의 요청/응답 스키마 정의

**작성해야 할 코드**:

```python
from pydantic import BaseModel, Field
from typing import Optional, List

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    is_active: bool
    created_at: datetime
```

### 🛠️ **app/utils/** - 유틸리티

**역할**: 공통으로 사용되는 유틸리티 함수들

#### **app/utils/security.py** - 보안 유틸리티

**역할**: JWT 토큰, 비밀번호 해싱 등 보안 관련 기능

**작성해야 할 코드**:

```python
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

#### **app/utils/validators.py** - 유효성 검사

**역할**: 데이터 유효성 검사 함수들

**작성해야 할 코드**:

```python
import re
from typing import Optional

def validate_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    pattern = r'^01[0-9]-?[0-9]{4}-?[0-9]{4}$'
    return re.match(pattern, phone) is not None

def validate_password_strength(password: str) -> bool:
    # 최소 8자, 대소문자, 숫자, 특수문자 포함
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True
```

#### **app/utils/helpers.py** - 공통 유틸리티

**역할**: 공통으로 사용되는 헬퍼 함수들

**작성해야 할 코드**:

```python
import uuid
from datetime import datetime
from typing import Any, Dict

def generate_uuid() -> str:
    return str(uuid.uuid4())

def format_datetime(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def paginate_query(query, skip: int = 0, limit: int = 10):
    return query.offset(skip).limit(limit)

def create_response(data: Any, message: str = None) -> Dict:
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.now()
    }
```

### 🧪 **tests/** - 테스트 코드

**역할**: 단위 테스트, 통합 테스트, API 테스트

#### **tests/conftest.py** - 테스트 설정

**역할**: 테스트에 필요한 공통 설정 및 픽스처

**작성해야 할 코드**:

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config.database import get_db

client = TestClient(app)

@pytest.fixture
def test_db():
    # 테스트용 데이터베이스 설정
    pass

@pytest.fixture
def test_user():
    return {
        "user_id": "test_user_id",
        "username": "test_user",
        "email": "test@example.com"
    }
```

#### **tests/test_auth/** - 인증 테스트

**역할**: 인증 관련 API 테스트

**작성해야 할 코드**:

```python
import pytest
from fastapi.testclient import TestClient

def test_login_success(client: TestClient):
    response = client.post("/api/v1/auth/login", json={
        "username": "test_user",
        "password": "test_password"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_credentials(client: TestClient):
    response = client.post("/api/v1/auth/login", json={
        "username": "invalid_user",
        "password": "invalid_password"
    })
    assert response.status_code == 401
```

### 📄 **기타 파일들**

#### **requirements.txt** - 의존성 패키지

**역할**: 프로젝트에 필요한 Python 패키지 목록

**작성해야 할 내용**:

```
fastapi==0.117.1
uvicorn[standard]==0.36.0
sqlalchemy==2.0.36
alembic==1.14.0
asyncpg==0.30.0
python-jose[cryptography]==3.5.0
passlib[bcrypt]==1.7.4
python-dotenv==1.1.1
pydantic==2.11.9
pydantic-settings==2.6.1
pytest==8.3.4
pytest-asyncio==0.24.0
httpx==0.28.1
```

#### **env.example** - 환경 변수 템플릿

**역할**: 환경 변수 설정 예시

**작성해야 할 내용**:

```
# 앱 설정
APP_NAME=ModelAgencyBe
DEBUG=True

# 데이터베이스
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

# JWT 설정
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS 설정
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

#### **.gitignore** - Git 무시 파일

**역할**: Git에서 추적하지 않을 파일 목록

**작성해야 할 내용**:

```
# Python
__pycache__/
*.py[cod]
venv/
.env

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

## 아키텍처

이 프로젝트는 계층형 아키텍처(Layered Architecture)를 따릅니다:

- **API Layer**: FastAPI 라우터, 요청/응답 처리
- **Service Layer**: 비즈니스 로직 처리
- **Repository Layer**: 데이터 접근 및 영속성 관리
- **Model Layer**: 데이터 모델 정의

## 설치 및 실행

### 1. 가상환경 설정

```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

```bash
# env.example을 .env로 복사
cp env.example .env

# .env 파일을 편집하여 실제 값으로 변경
```

### 4. 서버 실행

```bash
# 개발 모드로 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 또는 직접 실행
python app/main.py
```

### 5. API 문서 확인

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 엔드포인트

### 인증 (Authentication)

- `POST /api/v1/auth/login` - 로그인
- `POST /api/v1/auth/register` - 회원가입
- `POST /api/v1/auth/refresh` - 토큰 갱신
- `POST /api/v1/auth/logout` - 로그아웃
- `GET /api/v1/auth/me` - 현재 사용자 정보

### 모델 관리 (Models)

- `GET /api/v1/models/` - 모델 목록 조회
- `GET /api/v1/models/{model_id}` - 모델 상세 조회
- `POST /api/v1/models/` - 모델 등록 (관리자)
- `PUT /api/v1/models/{model_id}` - 모델 수정 (관리자)
- `DELETE /api/v1/models/{model_id}` - 모델 삭제 (관리자)

### 예약 관리 (Bookings)

- `GET /api/v1/bookings/` - 예약 목록 조회
- `GET /api/v1/bookings/{booking_id}` - 예약 상세 조회
- `POST /api/v1/bookings/` - 예약 생성
- `PUT /api/v1/bookings/{booking_id}` - 예약 수정
- `DELETE /api/v1/bookings/{booking_id}` - 예약 취소

## ORM 추천

### 1. SQLAlchemy (관계형 데이터베이스)

```bash
pip install sqlalchemy alembic asyncpg  # PostgreSQL
pip install sqlalchemy alembic aiomysql  # MySQL
```

**장점:**

- 성숙한 ORM, 풍부한 기능
- 다양한 데이터베이스 지원
- 마이그레이션 도구 (Alembic) 제공

### 2. Tortoise ORM (비동기 지원)

```bash
pip install tortoise-orm asyncpg
```

**장점:**

- Django ORM과 유사한 문법
- 완전한 비동기 지원
- 자동 마이그레이션

### 3. Beanie (MongoDB)

```bash
pip install beanie motor
```

**장점:**

- MongoDB 전용
- Pydantic 기반
- 비동기 지원

## 🚀 개발 가이드

### 📝 새로운 API 추가하기

새로운 도메인(예: `users`)을 추가하는 단계별 가이드:

#### 1단계: 폴더 구조 생성

```bash
mkdir -p app/api/v1/users
touch app/api/v1/users/__init__.py
touch app/api/v1/users/router.py
touch app/api/v1/users/schemas.py
```

#### 2단계: 스키마 정의 (`app/api/v1/users/schemas.py`)

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="이메일")
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=100)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, description="이메일")
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    full_name: str
    is_active: bool
    created_at: datetime
```

#### 3단계: ORM 모델 생성 (`app/models/user.py`)

```python
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### 4단계: 리포지토리 구현 (`app/repository/user_repository.py`)

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
from app.repository.base import BaseCRUDRepository
from typing import Optional, List

class UserRepository(BaseCRUDRepository[User, str]):
    def __init__(self, db: AsyncSession):
        super().__init__(User)
        self.db = db

    async def create(self, user_data: UserCreate) -> User:
        db_user = User(**user_data.dict())
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
```

#### 5단계: 서비스 구현 (`app/service/user_service.py`)

```python
from app.repository.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.core.exceptions import UserNotFoundException, ValidationException
from app.utils.security import get_password_hash, verify_password
from typing import Optional, List

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def create_user(self, user_data: UserCreate) -> dict:
        # 중복 검사
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise ValidationException("이미 존재하는 이메일입니다")

        existing_username = await self.user_repo.get_by_username(user_data.username)
        if existing_username:
            raise ValidationException("이미 존재하는 사용자명입니다")

        # 비밀번호 해싱
        hashed_password = get_password_hash(user_data.password)
        user_data.hashed_password = hashed_password

        # 사용자 생성
        user = await self.user_repo.create(user_data)
        return {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": user.created_at
        }

    async def get_user_by_id(self, user_id: str) -> dict:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)

        return {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": user.created_at
        }
```

#### 6단계: 라우터 구현 (`app/api/v1/users/router.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.dependencies import get_current_user, get_admin_user
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.service.user_service import UserService
from app.repository.user_repository import UserRepository
from app.config.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    user_repo = UserRepository(db)
    return UserService(user_repo)

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """새 사용자 생성"""
    return await user_service.create_user(user_data)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_current_user)
):
    """사용자 정보 조회"""
    return await user_service.get_user_by_id(user_id)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_admin_user)
):
    """사용자 정보 수정 (관리자만)"""
    return await user_service.update_user(user_id, user_data)

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: dict = Depends(get_admin_user)
):
    """사용자 삭제 (관리자만)"""
    await user_service.delete_user(user_id)
    return {"message": "사용자가 삭제되었습니다"}
```

#### 7단계: 메인 라우터에 등록 (`app/api/v1/router.py`)

```python
from app.api.v1.users.router import router as users_router

# 기존 라우터들...
api_router.include_router(
    users_router,
    prefix="/users",
    tags=["사용자 관리"]
)
```

### 🔧 의존성 주입 패턴

#### 기본 의존성 사용

```python
from fastapi import Depends
from app.core.dependencies import get_current_user, get_admin_user

@router.get("/protected")
async def protected_route(user = Depends(get_current_user)):
    return {"user": user}

@router.get("/admin-only")
async def admin_route(admin = Depends(get_admin_user)):
    return {"admin": admin}
```

#### 커스텀 의존성 생성

```python
from fastapi import Depends
from app.repository.user_repository import UserRepository
from app.service.user_service import UserService

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    user_repo = UserRepository(db)
    return UserService(user_repo)

@router.post("/users")
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.create_user(user_data)
```

### ⚠️ 예외 처리 패턴

#### 커스텀 예외 사용

```python
from app.core.exceptions import UserNotFoundException, ValidationException

async def get_user_by_id(user_id: str):
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UserNotFoundException(user_id)
    return user

async def create_user(user_data: UserCreate):
    if user_data.age < 18:
        raise ValidationException("18세 이상만 가입 가능합니다")
    # ... 나머지 로직
```

#### 예외 핸들러 등록 (`app/main.py`)

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.exceptions import ModelAgencyException

@app.exception_handler(ModelAgencyException)
async def model_agency_exception_handler(request: Request, exc: ModelAgencyException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error_code": exc.__class__.__name__,
            "error_message": exc.message,
            "timestamp": datetime.now()
        }
    )
```

### 📊 데이터베이스 마이그레이션 (Alembic)

#### 마이그레이션 초기화

```bash
# Alembic 초기화
alembic init alembic

# 마이그레이션 파일 생성
alembic revision --autogenerate -m "Create users table"

# 마이그레이션 실행
alembic upgrade head
```

#### 마이그레이션 파일 예시 (`alembic/versions/xxx_create_users_table.py`)

```python
def upgrade():
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
```

### 🧪 테스트 작성 패턴

#### API 테스트 예시 (`tests/test_users.py`)

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user_success():
    response = client.post("/api/v1/users/", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == "test@example.com"

def test_create_user_duplicate_email():
    # 첫 번째 사용자 생성
    client.post("/api/v1/users/", json={
        "username": "user1",
        "email": "duplicate@example.com",
        "password": "password",
        "full_name": "User 1"
    })

    # 동일한 이메일로 두 번째 사용자 생성 시도
    response = client.post("/api/v1/users/", json={
        "username": "user2",
        "email": "duplicate@example.com",
        "password": "password",
        "full_name": "User 2"
    })
    assert response.status_code == 422
    assert "이미 존재하는 이메일" in response.json()["detail"]
```

### 🔒 보안 구현 패턴

#### JWT 토큰 생성 및 검증

```python
from app.utils.security import create_access_token, verify_token
from datetime import timedelta

# 토큰 생성
def create_user_token(user_id: str, username: str):
    data = {
        "sub": user_id,
        "username": username
    }
    expires_delta = timedelta(minutes=30)
    return create_access_token(data, expires_delta)

# 토큰 검증
def verify_user_token(token: str):
    payload = verify_token(token)
    if not payload:
        raise AuthenticationException("유효하지 않은 토큰입니다")
    return payload
```

#### 비밀번호 검증

```python
from app.utils.security import verify_password, get_password_hash

# 비밀번호 해싱
hashed_password = get_password_hash("plain_password")

# 비밀번호 검증
is_valid = verify_password("plain_password", hashed_password)
```

### 📈 성능 최적화 팁

#### 데이터베이스 쿼리 최적화

```python
# N+1 문제 해결을 위한 조인 사용
async def get_users_with_bookings():
    result = await db.execute(
        select(User)
        .options(selectinload(User.bookings))
        .where(User.is_active == True)
    )
    return result.scalars().all()

# 페이징 구현
async def get_users_paginated(skip: int = 0, limit: int = 10):
    result = await db.execute(
        select(User)
        .offset(skip)
        .limit(limit)
        .order_by(User.created_at.desc())
    )
    return result.scalars().all()
```

#### 캐싱 구현

```python
from functools import lru_cache
import redis

# 메모리 캐싱
@lru_cache(maxsize=128)
def get_user_by_id_cached(user_id: str):
    return user_repo.get_by_id(user_id)

# Redis 캐싱
redis_client = redis.Redis(host='localhost', port=6379, db=0)

async def get_user_with_cache(user_id: str):
    # 캐시에서 먼저 확인
    cached_user = redis_client.get(f"user:{user_id}")
    if cached_user:
        return json.loads(cached_user)

    # 캐시에 없으면 DB에서 조회
    user = await user_repo.get_by_id(user_id)
    if user:
        redis_client.setex(f"user:{user_id}", 300, json.dumps(user.dict()))

    return user
```

## 🧪 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_auth.py

# 커버리지 포함 테스트
pytest --cov=app --cov-report=html

# 비동기 테스트 실행
pytest -v tests/test_async.py
```

## 🚀 배포 가이드

### Docker 사용

#### Dockerfile 생성

```dockerfile
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose 설정

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - '8000:8000'
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/modelagency
    depends_on:
      - db
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=modelagency
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - '5432:5432'
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 환경별 설정

#### 개발 환경

```bash
# .env.development
DEBUG=True
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/modelagency_dev
SECRET_KEY=dev-secret-key
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

#### 스테이징 환경

```bash
# .env.staging
DEBUG=False
DATABASE_URL=postgresql+asyncpg://user:password@staging-db:5432/modelagency_staging
SECRET_KEY=staging-secret-key
ALLOWED_ORIGINS=https://staging.example.com
```

#### 프로덕션 환경

```bash
# .env.production
DEBUG=False
DATABASE_URL=postgresql+asyncpg://user:password@prod-db:5432/modelagency_prod
SECRET_KEY=production-secret-key-change-this
ALLOWED_ORIGINS=https://api.example.com
```

## 📚 추가 학습 자료

### FastAPI 공식 문서

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [FastAPI 튜토리얼](https://fastapi.tiangolo.com/tutorial/)
- [FastAPI 고급 사용법](https://fastapi.tiangolo.com/advanced/)

### SQLAlchemy 학습

- [SQLAlchemy 공식 문서](https://docs.sqlalchemy.org/)
- [SQLAlchemy 비동기 가이드](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)

### Pydantic 학습

- [Pydantic 공식 문서](https://docs.pydantic.dev/)
- [Pydantic 설정 관리](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

## 🔧 개발 도구 추천

### IDE 및 에디터

- **VS Code**: Python 확장, FastAPI 스니펫
- **PyCharm**: 강력한 Python IDE
- **Cursor**: AI 기반 코드 에디터

### 유용한 확장 프로그램

- **Python**: Microsoft Python 확장
- **Python Docstring Generator**: 자동 문서화
- **FastAPI**: FastAPI 스니펫
- **SQLAlchemy**: SQLAlchemy 지원

### 디버깅 도구

- **pdb**: Python 내장 디버거
- **ipdb**: 향상된 디버거
- **FastAPI Debug Toolbar**: 웹 디버깅 도구

## 🐛 문제 해결 가이드

### 자주 발생하는 문제들

#### 1. ImportError: No module named 'app'

```bash
# 해결방법: PYTHONPATH 설정
export PYTHONPATH="${PYTHONPATH}:/path/to/your/project"
# 또는
python -m app.main
```

#### 2. 데이터베이스 연결 오류

```python
# 해결방법: 연결 문자열 확인
DATABASE_URL = "postgresql+asyncpg://username:password@localhost:5432/dbname"
```

#### 3. CORS 오류

```python
# 해결방법: CORS 설정 확인
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 4. Pydantic 검증 오류

```python
# 해결방법: 스키마 정의 확인
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., description="이메일")
```

## 📈 성능 모니터링

### 로깅 설정

```python
import logging
from fastapi import FastAPI

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response
```

### 메트릭 수집

```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(duration)

    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## 🤝 기여 가이드

### 코드 스타일

- **PEP 8** 준수
- **Black** 코드 포맷터 사용
- **isort** import 정렬
- **flake8** 린터 사용

### 커밋 메시지 규칙

```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
style: 코드 스타일 변경
refactor: 코드 리팩토링
test: 테스트 추가/수정
chore: 빌드 설정 변경
```

### Pull Request 가이드

1. 기능 브랜치 생성
2. 코드 작성 및 테스트
3. 문서 업데이트
4. Pull Request 생성
5. 코드 리뷰 및 수정
6. 머지

## 📄 라이선스

MIT License

## 📞 지원 및 문의

- **이슈 리포트**: GitHub Issues 사용
- **기능 요청**: GitHub Discussions 사용
- **문서 개선**: Pull Request 제출

---

**Happy Coding! 🚀**
