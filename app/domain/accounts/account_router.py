from uuid import UUID

from fastapi import APIRouter, Depends

from app.domain.accounts.account_service import account_service
from app.shared.dependencies import get_current_user
from app.domain.accounts.account_schemas import (
    SignUpAdminRequest,
    SignUpDirectorRequest,
    UserResponse,
    LoginRequest,
    LoginResponse,
    PasswordChangeRequest,
    CurrentUserPasswordChangeRequest,
    AccountResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
)

app = APIRouter(
    prefix="/accounts",
    tags=["accounts"],
    responses={404: {"description": "Not found"}},
)


@app.post("/signup/admins", response_model=UserResponse, status_code=201)
async def create_admin(request: SignUpAdminRequest):
    """
    관리자 계정 생성
    
    - **name**: 관리자 이름
    - **pid**: 이메일 (고유, 중복 불가)
    - **password**: 비밀번호 (8-20자, 영문+숫자+특수문자)
    - **provider**: 가입 경로 (LOCAL/GOOGLE/KAKAO/NAVER)
    - **provider_id**: 소셜 로그인 ID (선택)
    """
    return await account_service.signup_admin(request)


@app.post("/signup/directors", response_model=UserResponse, status_code=201)
async def create_director(request: SignUpDirectorRequest):
    """
    감독 계정 생성
    
    - **name**: 감독 이름
    - **pid**: 이메일 (고유, 중복 불가)
    - **password**: 비밀번호 (8-20자, 영문+숫자+특수문자)
    - **provider**: 가입 경로 (LOCAL/GOOGLE/KAKAO/NAVER)
    - **provider_id**: 소셜 로그인 ID (선택)
    """
    return await account_service.signup_director(request)


@app.post("/password/admins", response_model=AccountResponse)
async def change_admins_password(request: PasswordChangeRequest):
    """
    관리자 계정 비밀번호 변경
    
    - **pid**: 이메일
    - **current_password**: 현재 비밀번호
    - **new_password**: 새 비밀번호 (8-20자, 영문+숫자+특수문자)
    """
    return await account_service.change_password(request)


@app.post("/password/directors", response_model=AccountResponse)
async def change_directors_password(request: PasswordChangeRequest):
    """
    감독 계정 비밀번호 변경
    
    - **pid**: 이메일
    - **current_password**: 현재 비밀번호
    - **new_password**: 새 비밀번호 (8-20자, 영문+숫자+특수문자)
    """
    return await account_service.change_password(request)


@app.delete("/directors/{director_id}", response_model=AccountResponse)
async def withdraw_director(director_id: UUID):
    """
    감독 계정 삭제
    
    - **director_id**: 삭제할 감독 계정의 UUID
    """
    return await account_service.delete_account(director_id)


@app.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    로그인
    
    - **pid**: 이메일
    - **password**: 비밀번호
    
    **Returns**:
    - **access_token**: JWT 액세스 토큰 (유효기간: 4시간)
    - **refresh_token**: JWT 리프레시 토큰 (유효기간: 3일)
    - **token_type**: bearer
    - **user**: 사용자 정보
    """
    return await account_service.login(request)


@app.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    토큰 갱신
    
    액세스 토큰이 만료되었을 때 리프레시 토큰으로 새로운 토큰을 발급받습니다.
    
    - **refresh_token**: 유효한 리프레시 토큰
    
    **Returns**:
    - **access_token**: 새로운 JWT 액세스 토큰 (유효기간: 4시간)
    - **refresh_token**: 새로운 JWT 리프레시 토큰 (유효기간: 3일)
    - **token_type**: bearer
    
    **Note**: 보안을 위해 리프레시 토큰도 함께 갱신됩니다.
    """
    return await account_service.refresh_access_token(request)


@app.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    현재 로그인한 사용자 정보 조회
    
    - **Authorization**: Bearer token 필요
    
    **Returns**:
    - **id**: 사용자 고유 ID
    - **name**: 사용자 이름
    - **pid**: 이메일
    - **role**: 사용자 역할 (ADMIN/DIRECTOR)
    - **provider**: 가입 경로 (LOCAL/GOOGLE/KAKAO/NAVER)
    - **created_at**: 가입일시
    """
    return await account_service.get_user_profile(current_user["pid"])


@app.put("/me/password", response_model=AccountResponse)
async def change_current_user_password(
    request: CurrentUserPasswordChangeRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    현재 로그인한 사용자의 비밀번호 변경
    
    - **Authorization**: Bearer token 필요
    
    - **current_password**: 현재 비밀번호
    - **new_password**: 새 비밀번호 (8-20자, 영문+숫자+특수문자)
    
    **Returns**:
    - **message**: 성공 메시지
    """
    return await account_service.change_current_user_password(
        current_user["pid"], 
        request.current_password, 
        request.new_password
    )