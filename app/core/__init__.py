"""
핵심 설정 및 공통 기능
Spring Boot의 @Configuration과 유사
"""

from .config import settings
from .database import get_db, Base
from .exceptions import (
    ModelAgencyException,
    ModelNotFoundException,
    ValidationException,
    AuthenticationException,
    AuthorizationException
)

# 공개 API
__all__ = [
    "settings",
    "get_db", "Base",
    "ModelAgencyException",
    "ModelNotFoundException", 
    "ValidationException",
    "AuthenticationException",
    "AuthorizationException"
]
