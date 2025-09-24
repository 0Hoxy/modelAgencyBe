"""
모델 도메인 패키지
Spring Boot의 패키지와 동일한 역할
"""

# 주요 컴포넌트들을 패키지 레벨에서 import 가능하게 함
from .router import router
from .services import ModelService, PortfolioService
from .schemas import (
    ModelCreate, ModelUpdate, ModelResponse, ModelList,
    PortfolioCreate, PortfolioUpdate, PortfolioResponse, PortfolioList
)
from .repositories import ModelRepository, PortfolioRepository
from .models import Model, Portfolio

# 공개 API 정의 (Spring Boot의 @Component와 유사)
__all__ = [
    "router",
    "ModelService", 
    "PortfolioService",
    "ModelCreate", "ModelUpdate", "ModelResponse", "ModelList",
    "PortfolioCreate", "PortfolioUpdate", "PortfolioResponse", "PortfolioList",
    "ModelRepository", "PortfolioRepository",
    "Model", "Portfolio"
]
