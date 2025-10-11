
from uuid import UUID

from fastapi import HTTPException

from app.core.db import db
from app.domain.accounts.account_repository import account_repository
from app.domain.accounts.account_schemas import (
    SignUpRequest,
    SignUpAdminRequest,
    SignUpDirectorRequest,
    UserResponse,
    LoginRequest,
    LoginResponse,
    PasswordChangeRequest,
    AccountResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
)
from app.shared.security import password_hasher, jwt_handler


class AccountService:
    """계정 서비스 로직"""

    def __init__(self, repository):
        self.repository = repository

    async def signup(self, signup_data: SignUpRequest) -> UserResponse:
        """
        회원가입 (일반)
        
        Args:
            signup_data: 회원가입 데이터
            
        Returns:
            UserResponse: 생성된 사용자 정보
            
        Raises:
            HTTPException: 중복된 이메일 또는 DB 오류
        """
        try:
            # 이메일 중복 확인
            if await self.repository.check_pid_exists(signup_data.pid):
                raise HTTPException(
                    status_code=400,
                    detail="이미 사용 중인 이메일입니다."
                )

            # 비밀번호 해싱
            hashed_password = password_hasher.hash_password(signup_data.password)

            # 계정 생성 (트랜잭션)
            async with db.transaction() as conn:
                data_dict = signup_data.model_dump(exclude={'password'})
                data_dict['password'] = hashed_password

                result = await self.repository.create_account_transaction(conn, data_dict)

                if not result:
                    raise HTTPException(
                        status_code=500,
                        detail="계정 생성에 실패했습니다."
                    )

                return UserResponse.model_validate(dict(result))

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"회원가입 중 오류가 발생했습니다: {str(e)}"
            )

    async def signup_admin(self, signup_data: SignUpAdminRequest) -> UserResponse:
        """
        관리자 회원가입
        
        Args:
            signup_data: 관리자 회원가입 데이터
            
        Returns:
            UserResponse: 생성된 관리자 정보
        """
        return await self.signup(signup_data)

    async def signup_director(self, signup_data: SignUpDirectorRequest) -> UserResponse:
        """
        감독 회원가입
        
        Args:
            signup_data: 감독 회원가입 데이터
            
        Returns:
            UserResponse: 생성된 감독 정보
        """
        return await self.signup(signup_data)

    async def login(self, login_data: LoginRequest) -> LoginResponse:
        """
        로그인
        
        Args:
            login_data: 로그인 데이터
            
        Returns:
            LoginResponse: JWT 토큰(액세스+리프레시)과 사용자 정보
            
        Raises:
            HTTPException: 잘못된 이메일/비밀번호
        """
        try:
            # 사용자 조회
            user = await self.repository.get_by_pid(login_data.pid)

            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="이메일 또는 비밀번호가 올바르지 않습니다."
                )

            # 비밀번호 검증
            if not password_hasher.verify_password(
                login_data.password,
                user['password']
            ):
                raise HTTPException(
                    status_code=401,
                    detail="이메일 또는 비밀번호가 올바르지 않습니다."
                )

            # JWT 액세스 토큰 생성
            access_token_data = {
                "sub": user['pid'],  # subject (주체)
                "user_id": str(user['id']),
                "role": user['role'],
            }
            access_token = jwt_handler.create_access_token(access_token_data)

            # JWT 리프레시 토큰 생성 (최소 정보만 포함)
            refresh_token_data = {
                "sub": user['pid'],
            }
            refresh_token = jwt_handler.create_refresh_token(refresh_token_data)

            # 사용자 정보 (password 제외)
            user_response = UserResponse.model_validate(dict(user))

            return LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                user=user_response
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"로그인 중 오류가 발생했습니다: {str(e)}"
            )

    async def change_password(
        self,
        change_data: PasswordChangeRequest
    ) -> AccountResponse:
        """
        비밀번호 변경
        
        Args:
            change_data: 비밀번호 변경 데이터
            
        Returns:
            AccountResponse: 성공 메시지
            
        Raises:
            HTTPException: 잘못된 현재 비밀번호 또는 DB 오류
        """
        try:
            # 사용자 조회
            user = await self.repository.get_by_pid(change_data.pid)

            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="사용자를 찾을 수 없습니다."
                )

            # 현재 비밀번호 검증
            if not password_hasher.verify_password(
                change_data.current_password,
                user['password']
            ):
                raise HTTPException(
                    status_code=401,
                    detail="현재 비밀번호가 올바르지 않습니다."
                )

            # 새 비밀번호 해싱
            new_hashed_password = password_hasher.hash_password(
                change_data.new_password
            )

            # 비밀번호 업데이트 (트랜잭션)
            async with db.transaction() as conn:
                result = await self.repository.update_password_transaction(
                    conn,
                    change_data.pid,
                    new_hashed_password
                )

                if not result:
                    raise HTTPException(
                        status_code=500,
                        detail="비밀번호 변경에 실패했습니다."
                    )

            return AccountResponse(message="비밀번호가 성공적으로 변경되었습니다.")

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"비밀번호 변경 중 오류가 발생했습니다: {str(e)}"
            )

    async def delete_account(self, account_id: UUID) -> AccountResponse:
        """
        계정 삭제
        
        Args:
            account_id: 계정 ID
            
        Returns:
            AccountResponse: 성공 메시지
            
        Raises:
            HTTPException: 계정을 찾을 수 없음 또는 DB 오류
        """
        try:
            async with db.transaction() as conn:
                result = await self.repository.delete_by_id_transaction(
                    conn,
                    str(account_id)
                )

                if not result:
                    raise HTTPException(
                        status_code=404,
                        detail="계정을 찾을 수 없습니다."
                    )

            return AccountResponse(
                message=f"{result['name']} 계정이 성공적으로 삭제되었습니다."
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"계정 삭제 중 오류가 발생했습니다: {str(e)}"
            )

    async def refresh_access_token(
        self,
        refresh_request: RefreshTokenRequest
    ) -> RefreshTokenResponse:
        """
        리프레시 토큰으로 새로운 액세스 토큰 발급
        
        Args:
            refresh_request: 리프레시 토큰 요청
            
        Returns:
            RefreshTokenResponse: 새로운 액세스 토큰과 리프레시 토큰
            
        Raises:
            HTTPException: 유효하지 않은 토큰 또는 사용자를 찾을 수 없음
        """
        try:
            # 리프레시 토큰 검증
            payload = jwt_handler.verify_token(
                refresh_request.refresh_token,
                token_type="refresh"
            )

            if not payload:
                raise HTTPException(
                    status_code=401,
                    detail="유효하지 않거나 만료된 리프레시 토큰입니다."
                )

            # 사용자 조회
            pid = payload.get("sub")
            user = await self.repository.get_by_pid(pid)

            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="사용자를 찾을 수 없습니다."
                )

            # 새로운 액세스 토큰 생성
            access_token_data = {
                "sub": user['pid'],
                "user_id": str(user['id']),
                "role": user['role'],
            }
            new_access_token = jwt_handler.create_access_token(access_token_data)

            # 새로운 리프레시 토큰 생성 (보안을 위해 갱신)
            refresh_token_data = {
                "sub": user['pid'],
            }
            new_refresh_token = jwt_handler.create_refresh_token(refresh_token_data)

            return RefreshTokenResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"토큰 갱신 중 오류가 발생했습니다: {str(e)}"
            )
    
    async def get_user_profile(self, pid: str) -> UserResponse:
        """
        사용자 프로필 조회
        """
        try:
            user = await self.repository.get_by_pid(pid)
            if not user:
                raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
            return UserResponse.model_validate(dict(user))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"사용자 정보 조회 중 오류가 발생했습니다: {str(e)}")
    
    async def change_current_user_password(self, pid: str, current_password: str, new_password: str) -> AccountResponse:
        """
        현재 로그인한 사용자의 비밀번호 변경
        """
        try:
            # 현재 비밀번호 검증
            is_valid = await self.repository.verify_password(pid, current_password)
            if not is_valid:
                raise HTTPException(status_code=400, detail="현재 비밀번호가 올바르지 않습니다.")
            
            # 새 비밀번호로 업데이트
            await self.repository.change_password_with_transaction(pid, new_password)
            
            return AccountResponse(message="비밀번호가 성공적으로 변경되었습니다.")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"비밀번호 변경 중 오류가 발생했습니다: {str(e)}")


account_service = AccountService(account_repository)
