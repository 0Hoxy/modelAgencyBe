"""
커스텀 예외 클래스들
"""

class ModelAgencyException(Exception):
    """기본 예외 클래스"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ModelNotFoundException(ModelAgencyException):
    """모델을 찾을 수 없을 때 발생하는 예외"""
    def __init__(self, model_id: str):
        super().__init__(
            message=f"모델을 찾을 수 없습니다: {model_id}",
            status_code=404
        )


class ValidationException(ModelAgencyException):
    """유효성 검사 실패 시 발생하는 예외"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=400
        )


class AuthenticationException(ModelAgencyException):
    """인증 실패 시 발생하는 예외"""
    def __init__(self, message: str = "인증에 실패했습니다"):
        super().__init__(
            message=message,
            status_code=401
        )


class AuthorizationException(ModelAgencyException):
    """권한 부족 시 발생하는 예외"""
    def __init__(self, message: str = "권한이 없습니다"):
        super().__init__(
            message=message,
            status_code=403
        )
