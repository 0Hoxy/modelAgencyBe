"""
로깅 관련 유틸리티 및 공통 기능
"""
import logging
import sys
from functools import wraps
from typing import Any, Callable
from sqlalchemy.exc import SQLAlchemyError


def setup_logging(level: str = "INFO") -> None:
    """
    애플리케이션 전체 로깅 설정을 초기화합니다.

    Args:
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            # 필요시 파일 핸들러도 추가 가능
            # logging.FileHandler('app.log')
        ]
    )


def get_repository_logger(domain_name: str) -> logging.Logger:
    """
    Repository용 도메인별 로거를 생성합니다.

    Args:
        domain_name: 도메인 이름 (예: "model", "user", "account")

    Returns:
        logging.Logger: 도메인별 로거

    Example:
        logger = get_repository_logger("model")
        # 로거 이름: "repository.model"
    """
    return logging.getLogger(f"repository.{domain_name}")


def log_db_operation(operation: str):
    """
    데이터베이스 작업을 로깅하는 데코레이터입니다.

    ⚠️  주의: handle_repository_exceptions 데코레이터와 함께 사용할 때
            예외 처리는 handle_repository_exceptions에서만 수행되므로
            이 데코레이터에서는 로깅만 담당합니다.

    Args:
        operation: 작업 유형 (CREATE, READ, UPDATE, DELETE 등)

    Example:
        @log_db_operation("CREATE")
        @handle_repository_exceptions
        async def create(self, db: AsyncSession, data: CreateModel):
            # 데이터베이스 생성 작업
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs) -> Any:
            # Repository의 로거 사용
            logger = getattr(self, 'logger', logging.getLogger(__name__))

            logger.info(f"[{operation}] 시작 - 메서드: {func.__name__}")

            try:
                result = await func(self, *args, **kwargs)
                logger.info(f"[{operation}] 성공 - 메서드: {func.__name__}")
                return result
            except Exception:
                # 예외는 재발생시키되, 로그는 handle_repository_exceptions에서 처리
                logger.debug(f"[{operation}] 예외 발생 - 메서드: {func.__name__} (상세 로그는 예외 처리기에서 기록됨)")
                raise

        return wrapper
    return decorator


def log_service_operation(operation: str):
    """
    서비스 레이어 작업을 로깅하는 데코레이터입니다.

    비즈니스 로직 처리의 시작/완료/실패를 자동으로 로깅합니다.

    Args:
        operation: 작업 유형 (PROCESS, VALIDATE, CALCULATE 등)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs) -> Any:
            # Service의 로거 사용
            logger = getattr(self, 'logger', logging.getLogger(__name__))

            try:
                logger.info(f"[{operation}] 서비스 시작 - 메서드: {func.__name__}")
                result = await func(self, *args, **kwargs)
                logger.info(f"[{operation}] 서비스 성공 - 메서드: {func.__name__}")
                return result

            except Exception as e:
                logger.error(f"[{operation}] 서비스 오류 - 메서드: {func.__name__}, 오류: {str(e)}")
                raise

        return wrapper
    return decorator


def get_service_logger(domain_name: str) -> logging.Logger:
    """
    Service용 도메인별 로거를 생성합니다.

    Args:
        domain_name: 도메인 이름 (예: "model", "user", "account")

    Returns:
        logging.Logger: 도메인별 로거
    """
    return logging.getLogger(f"service.{domain_name}")


class LoggerMixin:
    """
    로거 기능을 제공하는 믹스인 클래스입니다.

    Repository나 Service 클래스에서 상속받아 사용할 수 있습니다.
    """

    def __init__(self, domain_name: str, layer: str = "repository"):
        """
        Args:
            domain_name: 도메인 이름
            layer: 레이어 이름 ("repository" 또는 "service")
        """
        self.logger = logging.getLogger(f"{layer}.{domain_name}")
        self.logger.info(f"{layer.title()}({domain_name}) 초기화 완료")