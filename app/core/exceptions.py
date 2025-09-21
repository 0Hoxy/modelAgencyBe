"""
커스텀 예외 클래스들
비즈니스 로직에 맞는 예외 처리
"""

from fastapi import HTTPException, status


class ModelAgencyException(Exception):
    """기본 예외 클래스"""
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UserNotFoundException(ModelAgencyException):
    """사용자를 찾을 수 없을 때"""
    def __init__(self, user_id: str = None):
        message = f"사용자를 찾을 수 없습니다: {user_id}" if user_id else "사용자를 찾을 수 없습니다"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ModelNotFoundException(ModelAgencyException):
    """모델을 찾을 수 없을 때"""
    def __init__(self, model_id: str = None):
        message = f"모델을 찾을 수 없습니다: {model_id}" if model_id else "모델을 찾을 수 없습니다"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class BookingNotFoundException(ModelAgencyException):
    """예약을 찾을 수 없을 때"""
    def __init__(self, booking_id: str = None):
        message = f"예약을 찾을 수 없습니다: {booking_id}" if booking_id else "예약을 찾을 수 없습니다"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class AuthenticationException(ModelAgencyException):
    """인증 실패 시"""
    def __init__(self, message: str = "인증에 실패했습니다"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationException(ModelAgencyException):
    """권한 부족 시"""
    def __init__(self, message: str = "권한이 없습니다"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class ValidationException(ModelAgencyException):
    """유효성 검사 실패 시"""
    def __init__(self, message: str = "입력 데이터가 유효하지 않습니다"):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class BusinessLogicException(ModelAgencyException):
    """비즈니스 로직 위반 시"""
    def __init__(self, message: str = "비즈니스 로직을 위반했습니다"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)
