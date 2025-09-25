"""
공통 의존성 및 유틸리티 함수들
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from .config import settings
from .database import get_db
from .exceptions import AuthenticationException, AuthorizationException


# JWT 토큰 관련 의존성
security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """JWT 토큰에서 현재 사용자 ID 추출"""
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise AuthenticationException("토큰에서 사용자 정보를 찾을 수 없습니다")
        return user_id
    except JWTError:
        raise AuthenticationException("유효하지 않은 토큰입니다")


async def get_optional_current_user_id(
    authorization: Optional[str] = Header(None)
) -> Optional[int]:
    """선택적 사용자 인증 (토큰이 없어도 허용)"""
    if not authorization or not authorization.startswith("Bearer "):
        return None

    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("sub")
        return user_id
    except JWTError:
        return None


# 페이징 의존성
class PaginationParams:
    def __init__(
        self,
        page: int = 1,
        size: int = 10,
        max_size: int = 100
    ):
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="페이지는 1 이상이어야 합니다"
            )
        if size < 1 or size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"페이지 크기는 1~{max_size} 사이여야 합니다"
            )

        self.page = page
        self.size = size
        self.offset = (page - 1) * size
        self.limit = size


def get_pagination_params(
    page: int = 1,
    size: int = 10
) -> PaginationParams:
    """페이징 파라미터 의존성"""
    return PaginationParams(page=page, size=size)


# 관리자 권한 확인
async def require_admin_role(
    current_user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """관리자 권한 필요한 엔드포인트용 의존성"""
    # TODO: 실제 사용자 역할 확인 로직 구현
    # user = await get_user_by_id(db, current_user_id)
    # if not user.is_admin:
    #     raise AuthorizationException("관리자 권한이 필요합니다")
    pass


# 파일 업로드 관련
def validate_file_size(file_size: int) -> bool:
    """파일 크기 검증"""
    return file_size <= settings.MAX_FILE_SIZE


def validate_file_type(filename: str, allowed_types: list[str]) -> bool:
    """파일 타입 검증"""
    if not filename:
        return False

    file_extension = filename.split('.')[-1].lower()
    return file_extension in allowed_types


# 이미지 파일 검증
IMAGE_ALLOWED_TYPES = ['jpg', 'jpeg', 'png', 'gif', 'webp']

def validate_image_file(filename: str, file_size: int) -> bool:
    """이미지 파일 검증"""
    return (
        validate_file_size(file_size) and
        validate_file_type(filename, IMAGE_ALLOWED_TYPES)
    )


# 문서 파일 검증
DOCUMENT_ALLOWED_TYPES = ['pdf', 'doc', 'docx', 'txt']

def validate_document_file(filename: str, file_size: int) -> bool:
    """문서 파일 검증"""
    return (
        validate_file_size(file_size) and
        validate_file_type(filename, DOCUMENT_ALLOWED_TYPES)
    )