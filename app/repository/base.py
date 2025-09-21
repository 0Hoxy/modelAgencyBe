"""
기본 리포지토리 클래스
공통 CRUD 작업을 정의하는 추상 클래스
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Generic, TypeVar
from pydantic import BaseModel

# 제네릭 타입 정의
T = TypeVar('T', bound=BaseModel)
ID = TypeVar('ID')


class BaseRepository(ABC, Generic[T, ID]):
    """기본 리포지토리 추상 클래스"""
    
    @abstractmethod
    async def create(self, obj_in: T) -> T:
        """객체 생성"""
        pass
    
    @abstractmethod
    async def get_by_id(self, id: ID) -> Optional[T]:
        """ID로 객체 조회"""
        pass
    
    @abstractmethod
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        """모든 객체 조회 (페이징, 필터링)"""
        pass
    
    @abstractmethod
    async def update(self, id: ID, obj_in: T) -> Optional[T]:
        """객체 수정"""
        pass
    
    @abstractmethod
    async def delete(self, id: ID) -> bool:
        """객체 삭제"""
        pass
    
    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """객체 개수 조회"""
        pass


class BaseCRUDRepository(BaseRepository[T, ID]):
    """CRUD 작업을 포함한 기본 리포지토리"""
    
    def __init__(self, model_class: type):
        self.model_class = model_class
    
    async def create(self, obj_in: T) -> T:
        """객체 생성"""
        # TODO: ORM을 사용한 실제 구현
        return obj_in
    
    async def get_by_id(self, id: ID) -> Optional[T]:
        """ID로 객체 조회"""
        # TODO: ORM을 사용한 실제 구현
        return None
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        """모든 객체 조회 (페이징, 필터링)"""
        # TODO: ORM을 사용한 실제 구현
        return []
    
    async def update(self, id: ID, obj_in: T) -> Optional[T]:
        """객체 수정"""
        # TODO: ORM을 사용한 실제 구현
        return None
    
    async def delete(self, id: ID) -> bool:
        """객체 삭제"""
        # TODO: ORM을 사용한 실제 구현
        return False
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """객체 개수 조회"""
        # TODO: ORM을 사용한 실제 구현
        return 0
