# Model Agency Backend

FastAPI를 사용한 모델 에이전시 백엔드 API 서버입니다.

## 🎯 프로젝트 개요

모델 에이전시 플랫폼의 백엔드 API로, 모델(인물) 정보 관리, 포트폴리오 관리 등을 제공합니다.

> **입문자를 위한 안내**: 이 프로젝트는 Spring Boot 개발자가 FastAPI로 쉽게 전환할 수 있도록 설계되었습니다.

## 🏗️ 프로젝트 구조

### **핵심 개발 파일들 (Spring Boot와 동일한 개념)**

```
app/domains/models/             # 모델 도메인 (패키지)
├── models.py                   # 데이터베이스 모델 (@Entity)
├── schemas.py                  # DTO 클래스 (Request/Response)
├── repositories.py             # 데이터 접근 계층 (@Repository)
├── services.py                 # 비즈니스 로직 (@Service)
└── router.py                   # API 엔드포인트 (@RestController)
```

### **전체 프로젝트 구조**

```
modelAgencyBe/
├── app/
│   ├── main.py                 # 애플리케이션 진입점
│   ├── core/                   # 공통 설정 (config, database, exceptions)
│   ├── domains/models/         # 모델 도메인 (개발할 핵심 파일들)
│   └── shared/                 # 공통 유틸리티
├── requirements.txt            # 의존성 패키지
├── .env                        # 환경 변수
└── README.md
```

## 🚀 빠른 시작 가이드

### **1단계: 프로젝트 실행**

```bash
# 가상환경 활성화
source venv/bin/activate

# 서버 실행
uvicorn app.main:app --reload
```

### **2단계: API 문서 확인**

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### **3단계: API 테스트**

```bash
# 헬스 체크
curl http://localhost:8000/health

# 모델 목록 조회
curl http://localhost:8000/api/v1/models/
```

## 💡 Spring Boot 개발자를 위한 핵심 개념

### **파일 역할 비교**

| Spring Boot       | FastAPI           | 설명                     |
| ----------------- | ----------------- | ------------------------ |
| `@Entity`         | `models.py`       | 데이터베이스 테이블 정의 |
| `DTO`             | `schemas.py`      | 요청/응답 데이터 구조    |
| `@Repository`     | `repositories.py` | 데이터베이스 접근 로직   |
| `@Service`        | `services.py`     | 비즈니스 로직            |
| `@RestController` | `router.py`       | API 엔드포인트           |

### **개발 순서**

1. **models.py** - 데이터베이스 테이블 정의
2. **schemas.py** - 요청/응답 스키마 정의
3. **repositories.py** - 데이터 접근 로직 구현
4. **services.py** - 비즈니스 로직 구현
5. **router.py** - API 엔드포인트 구현

> **중요**: `__pycache__` 폴더와 `__init__.py` 파일은 신경쓰지 마세요! Python이 자동으로 관리합니다.

## 📊 API 엔드포인트

### **모델 관리 API**

- `GET /api/v1/models/` - 모델 목록 조회
- `GET /api/v1/models/{model_id}` - 모델 상세 조회
- `POST /api/v1/models/` - 모델 등록
- `PUT /api/v1/models/{model_id}` - 모델 수정
- `DELETE /api/v1/models/{model_id}` - 모델 삭제
- `GET /api/v1/models/search?q=검색어` - 모델 검색

### **포트폴리오 관리 API**

- `GET /api/v1/models/{model_id}/portfolios` - 모델의 포트폴리오 목록
- `POST /api/v1/models/portfolios` - 포트폴리오 생성
- `GET /api/v1/models/portfolios/featured` - 추천 포트폴리오
- `PUT /api/v1/models/portfolios/{portfolio_id}` - 포트폴리오 수정
- `DELETE /api/v1/models/portfolios/{portfolio_id}` - 포트폴리오 삭제

## 🔧 개발 팁

### **Spring Boot에서 FastAPI로 전환할 때**

1. **@RestController** → **APIRouter()**
2. **@GetMapping** → **@router.get()**
3. **@PostMapping** → **@router.post()**
4. **@PathVariable** → **Path(...)**
5. **@RequestParam** → **Query(...)**
6. **@RequestBody** → **함수 파라미터**

### **비동기 처리**

```python
# Spring Boot (동기)
@GetMapping("/users")
public List<User> getUsers() {
    return userService.getAllUsers();
}

# FastAPI (비동기)
@router.get("/users")
async def get_users():
    return await user_service.get_all_users()
```

## 🚀 새로운 도메인 추가하기

### **1단계: 폴더 생성**

```bash
mkdir -p app/domains/users
```

### **2단계: 파일 생성**

```bash
touch app/domains/users/models.py      # 데이터베이스 모델
touch app/domains/users/schemas.py     # DTO 클래스
touch app/domains/users/repositories.py # 데이터 접근
touch app/domains/users/services.py    # 비즈니스 로직
touch app/domains/users/router.py      # API 엔드포인트
```

### **3단계: 메인 라우터에 등록**

```python
# app/main.py에 추가
from app.domains.users.router import router as users_router
app.include_router(users_router, prefix="/api/v1/users")
```

> **팁**: Spring Boot에서 새로운 패키지를 만드는 것과 동일합니다!

## 📚 학습 자료

### **추천 학습 순서**

1. [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
2. [SQLAlchemy 문서](https://docs.sqlalchemy.org/)
3. [Pydantic 문서](https://docs.pydantic.dev/)

### **주요 차이점**

- **비동기 지원**: FastAPI는 기본적으로 비동기 처리
- **자동 문서화**: Swagger UI가 자동으로 생성됨
- **타입 힌팅**: Python의 타입 힌팅을 적극 활용

## 🚀 배포

### **Docker 사용**

```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 💡 개발 팁

### **Spring Boot에서 전환할 때 기억할 점**

1. **비동기 함수**: `async def` 사용
2. **타입 힌팅**: 모든 파라미터에 타입 명시
3. **자동 문서화**: 함수 docstring이 API 문서에 표시됨
4. **의존성 주입**: `Depends()` 사용

---

**🎉 이제 Spring Boot와 동일한 방식으로 FastAPI 개발을 시작하세요!**

> **핵심**: `models.py`, `schemas.py`, `repositories.py`, `services.py`, `router.py` 5개 파일만 신경쓰면 됩니다!
