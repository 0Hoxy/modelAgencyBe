"""
애플리케이션 전역 예외 클래스 및 예외 처리 유틸리티
"""
from typing import Any, Dict
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from functools import wraps


# =============================================================================
# 기본 예외 클래스
# =============================================================================

class ApplicationError(Exception):
    """애플리케이션 기본 예외 클래스"""

    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


# =============================================================================
# Repository 계층 예외
# =============================================================================

class RepositoryError(ApplicationError):
    """Repository 계층 기본 예외"""
    pass


class EntityNotFoundError(RepositoryError):
    """엔티티를 찾을 수 없을 때 발생하는 예외"""

    def __init__(self, entity_name: str, entity_id: Any):
        message = f"{entity_name}을(를) 찾을 수 없습니다 (ID: {entity_id})"
        super().__init__(
            message=message,
            error_code="ENTITY_NOT_FOUND",
            details={"entity_name": entity_name, "entity_id": entity_id}
        )


class EntityAlreadyExistsError(RepositoryError):
    """엔티티가 이미 존재할 때 발생하는 예외"""

    def __init__(self, entity_name: str, field_name: str, field_value: Any):
        message = f"{entity_name}이(가) 이미 존재합니다 ({field_name}: {field_value})"
        super().__init__(
            message=message,
            error_code="ENTITY_ALREADY_EXISTS",
            details={
                "entity_name": entity_name,
                "field_name": field_name,
                "field_value": field_value
            }
        )


class DatabaseConnectionError(RepositoryError):
    """데이터베이스 연결 오류"""

    def __init__(self, original_error: Exception = None):
        message = "데이터베이스 연결에 실패했습니다"
        super().__init__(
            message=message,
            error_code="DATABASE_CONNECTION_ERROR",
            details={"original_error": str(original_error) if original_error else None}
        )


class DatabaseConstraintError(RepositoryError):
    """데이터베이스 제약 조건 위반"""

    def __init__(self, constraint_name: str = None, original_error: Exception = None):
        message = f"데이터베이스 제약 조건 위반{f' ({constraint_name})' if constraint_name else ''}"
        super().__init__(
            message=message,
            error_code="DATABASE_CONSTRAINT_ERROR",
            details={
                "constraint_name": constraint_name,
                "original_error": str(original_error) if original_error else None
            }
        )


# =============================================================================
# Service 계층 예외
# =============================================================================

class ServiceError(ApplicationError):
    """Service 계층 기본 예외"""
    pass


class ValidationError(ServiceError):
    """비즈니스 로직 검증 실패"""

    def __init__(self, field_name: str, message: str, field_value: Any = None):
        super().__init__(
            message=f"{field_name}: {message}",
            error_code="VALIDATION_ERROR",
            details={
                "field_name": field_name,
                "field_value": field_value,
                "validation_message": message
            }
        )


class BusinessRuleError(ServiceError):
    """비즈니스 규칙 위반"""

    def __init__(self, rule_name: str, message: str):
        super().__init__(
            message=f"비즈니스 규칙 위반 - {rule_name}: {message}",
            error_code="BUSINESS_RULE_ERROR",
            details={"rule_name": rule_name, "rule_message": message}
        )


class ModelAgencyException(ApplicationError):
    """모델 에이전시 애플리케이션 기본 예외"""
    pass


class ModelNotFoundException(EntityNotFoundError):
    """모델을 찾을 수 없을 때 발생하는 예외"""

    def __init__(self, model_id: Any):
        super().__init__("모델", model_id)


class ValidationException(ValidationError):
    """검증 실패 예외"""
    pass


class AuthenticationException(ApplicationError):
    """인증 실패 예외"""

    def __init__(self, message: str = "인증에 실패했습니다"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationException(ApplicationError):
    """권한 부족 예외"""

    def __init__(self, message: str = "접근 권한이 없습니다"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR"
        )


# =============================================================================
# 예외 변환 함수
# =============================================================================

def convert_sqlalchemy_error(error: SQLAlchemyError) -> RepositoryError:
    """SQLAlchemy 예외를 애플리케이션 예외로 변환"""

    if isinstance(error, IntegrityError):
        # 제약 조건 위반 (중복 키, 외래 키 등)
        return DatabaseConstraintError(
            constraint_name=getattr(error.orig, 'diag', {}).get('constraint_name'),
            original_error=error
        )

    elif isinstance(error, NoResultFound):
        # 결과를 찾을 수 없음
        return EntityNotFoundError("엔티티", "unknown")

    else:
        # 기타 데이터베이스 오류
        return DatabaseConnectionError(error)


def convert_to_http_exception(error: ApplicationError) -> HTTPException:
    """애플리케이션 예외를 FastAPI HTTPException으로 변환"""

    status_code_map = {
        "ENTITY_NOT_FOUND": 404,
        "ENTITY_ALREADY_EXISTS": 409,
        "VALIDATION_ERROR": 422,
        "BUSINESS_RULE_ERROR": 400,
        "DATABASE_CONNECTION_ERROR": 503,
        "DATABASE_CONSTRAINT_ERROR": 409,
    }

    status_code = status_code_map.get(error.error_code, 500)

    return HTTPException(
        status_code=status_code,
        detail={
            "error_code": error.error_code,
            "message": error.message,
            "details": error.details
        }
    )


# =============================================================================
# 예외 처리 데코레이터
# =============================================================================

def handle_repository_exceptions(func):
    """
    Repository 메서드의 예외를 자동으로 변환하고 롤백을 처리하는 데코레이터

    쓰기 작업(CREATE, UPDATE, DELETE)에서 예외 발생 시 자동으로 롤백을 수행합니다.
    읽기 작업에서는 롤백을 수행하지 않습니다.
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # DB 세션 및 작업 유형 확인
        db_session = None
        operation_name = func.__name__.upper()
        is_write_operation = operation_name in ['CREATE', 'UPDATE', 'DELETE']

        if len(args) >= 2:
            # args[0]은 self, args[1]이 AsyncSession인지 타입 체크로 확인
            potential_db = args[1]
            if isinstance(potential_db, AsyncSession):
                db_session = potential_db

        # Repository의 로거 사용 (예외 로깅용)
        logger = None
        if len(args) >= 1 and hasattr(args[0], 'logger'):
            logger = args[0].logger

        try:
            return await func(*args, **kwargs)

        except SQLAlchemyError as e:
            # 데이터베이스 오류 발생 시 쓰기 작업이면 롤백
            if db_session and is_write_operation:
                await db_session.rollback()
                if logger:
                    logger.error(f"SQLAlchemy 오류로 롤백 수행 - 메서드: {func.__name__}, 오류: {str(e)}")
            elif logger:
                logger.error(f"SQLAlchemy 오류 - 메서드: {func.__name__}, 오류: {str(e)}")

            raise convert_sqlalchemy_error(e)

        except RepositoryError as e:
            # 이미 애플리케이션 예외인 경우 쓰기 작업이면 롤백 후 재발생
            if db_session and is_write_operation:
                await db_session.rollback()
                if logger:
                    logger.error(f"Repository 오류로 롤백 수행 - 메서드: {func.__name__}, 오류: {e.message}")
            elif logger:
                logger.error(f"Repository 오류 - 메서드: {func.__name__}, 오류: {e.message}")

            raise

        except Exception as e:
            # 예상하지 못한 예외 발생 시 쓰기 작업이면 롤백
            if db_session and is_write_operation:
                await db_session.rollback()
                if logger:
                    logger.error(f"예상치 못한 오류로 롤백 수행 - 메서드: {func.__name__}, 오류: {str(e)}")
            elif logger:
                logger.error(f"예상치 못한 오류 - 메서드: {func.__name__}, 오류: {str(e)}")

            # 예상하지 못한 예외는 일반적인 Repository 오류로 변환
            raise RepositoryError(
                message=f"Repository 작업 중 예기치 않은 오류가 발생했습니다: {str(e)}",
                error_code="UNEXPECTED_REPOSITORY_ERROR",
                details={"original_error": str(e), "error_type": type(e).__name__}
            )

    return wrapper


def handle_service_exceptions(func):
    """Service 메서드의 예외를 자동으로 처리하는 데코레이터"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        except RepositoryError:
            # Repository 예외는 그대로 전파
            raise

        except ServiceError:
            # 이미 Service 예외인 경우 그대로 재발생
            raise

        except Exception as e:
            # 예상하지 못한 예외는 일반적인 Service 오류로 변환
            raise ServiceError(
                message=f"Service 작업 중 예기치 않은 오류가 발생했습니다: {str(e)}",
                error_code="UNEXPECTED_SERVICE_ERROR",
                details={"original_error": str(e), "error_type": type(e).__name__}
            )

    return wrapper