import uuid
from typing import Dict, Any, Optional, List

import asyncpg

from app.core.db import db


class BaseRepository:
    """기본 Repository 클래스"""

    def __init__(self, table_name: str):
        """
        BaseRepository 초기화

        Args:
            table_name: 데이터베이스 테이블 이름
        """
        self.table_name = table_name

    async def create(self, data: Dict[str, Any]) -> Optional[asyncpg.Record]:
        """
        새로운 데이터를 생성합니다.

        Args:
            data: 생성할 데이터 (컬럼명: 값)
                  예: {"name": "홍길동", "email": "hong@example.com"}

        Returns:
            asyncpg.Record: 생성된 레코드 (모든 컬럼 포함)
            None: 생성 실패 시

        Raises:
            asyncpg.PostgresError: 데이터베이스 오류 발생 시
        """
        # Record = {Record name="홍길동", age=20, birth=1900-01-01}
        # Record.name, Record.age, Record.birth

        # Dict = [{name: "홍길동", age: 20, birth: 1900-01-01}, {name: "홍길동2", age: 20, birth: 1900-01-01}, {name: "홍길동3", age: 20, birth: 1900-01-01}]

        # data의 키들을 컬럼명으로 결합 (예: "name, email")
        columns = ", ".join(data.keys())
        # 파라미터 플레이스홀더 생성 (예: "$1, $2")
        placeholders = ", ".join(f"${i + 1}" for i in range(len(data)))
        # INSERT 쿼리 생성 및 생성된 레코드 반환
        query = f"""
            INSERT INTO {self.table_name} ({columns})
            VALUES ({placeholders})
            RETURNING id
        """
        return await db.fetchrow(query, *data.values())

    async def get_by_id(self, record_id: int) -> Optional[asyncpg.Record]:
        """
        ID로 단일 데이터를 조회합니다.

        Args:
            record_id: 조회할 레코드의 ID

        Returns:
            asyncpg.Record: 조회된 레코드
            None: 해당 ID의 레코드가 없을 경우

        Raises:
            asyncpg.PostgresError: 데이터베이스 오류 발생 시
        """
        # WHERE 절로 특정 ID의 레코드만 조회
        query = f"SELECT * FROM {self.table_name} WHERE id = $1"
        return await db.fetchrow(query, record_id)

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[asyncpg.Record]:
        """
        전체 데이터를 페이지네이션하여 조회합니다.

        Args:
            limit: 한 번에 조회할 최대 레코드 수 (기본값: 100)
            offset: 건너뛸 레코드 수 (기본값: 0)
                   예: offset=20이면 21번째 레코드부터 조회

        Returns:
            List[asyncpg.Record]: 조회된 레코드 리스트
            빈 리스트: 조회된 레코드가 없을 경우

        Raises:
            asyncpg.PostgresError: 데이터베이스 오류 발생 시
        """
        # LIMIT으로 최대 개수 제한, OFFSET으로 시작 위치 지정
        query = f"SELECT * FROM {self.table_name} LIMIT $1 OFFSET $2"
        return await db.fetch(query, limit, offset)

    async def update(self, record_id: int, data: Dict[str, Any]) -> Optional[asyncpg.Record]:
        """
        기존 데이터를 수정합니다.

        Args:
            record_id: 수정할 레코드의 ID
            data: 수정할 데이터 (컬럼명: 값)
                  예: {"name": "김철수", "email": "kim@example.com"}

        Returns:
            asyncpg.Record: 수정된 레코드 (모든 컬럼 포함)
            None: 해당 ID의 레코드가 없을 경우

        Raises:
            asyncpg.PostgresError: 데이터베이스 오류 발생 시

        Note:
            updated_at 컬럼이 있다면 자동으로 현재 시간으로 업데이트됩니다.
        """
        # SET 절 생성 (예: "name = $2, email = $3")
        # $1은 record_id이므로 $2부터 시작
        set_clause = ", ".join(f"{key} = ${i + 2}" for i, key in enumerate(data.keys()))
        # UPDATE 쿼리 실행 및 updated_at 자동 갱신
        query = f"""
            UPDATE {self.table_name}
            SET {set_clause}
            WHERE id = $1
            RETURNING $1
        """
        return await db.fetchrow(query, record_id, *data.values())

    async def delete(self, record_id: int) -> bool:
        """
        데이터를 삭제합니다.

        Args:
            record_id: 삭제할 레코드의 ID

        Returns:
            bool: True - 삭제 성공 (1개 레코드 삭제됨)
                  False - 삭제 실패 (해당 ID의 레코드 없음)

        Raises:
            asyncpg.PostgresError: 데이터베이스 오류 발생 시
        """
        # WHERE 절로 특정 ID의 레코드 삭제
        query = f"DELETE FROM {self.table_name} WHERE id = $1"
        result = await db.execute(query, record_id)
        # execute 결과가 "DELETE 1"이면 삭제 성공
        return result == "DELETE 1"

    async def exists(self, record_id: int) -> bool:
        """
        특정 ID의 레코드가 존재하는지 확인합니다.

        Args:
            record_id: 확인할 레코드의 ID

        Returns:
            bool: True - 레코드 존재
                  False - 레코드 없음

        Raises:
            asyncpg.PostgresError: 데이터베이스 오류 발생 시

        Note:
            EXISTS 쿼리를 사용하여 효율적으로 존재 여부만 확인합니다.
            전체 레코드를 가져오지 않으므로 성능상 유리합니다.
        """
        # EXISTS는 레코드 존재 여부만 True/False로 반환
        query = f"SELECT EXISTS(SELECT 1 FROM {self.table_name} WHERE id = $1)"
        result = await db.fetchrow(query, record_id)
        # result가 None이 아니면 exists 키의 값 반환, None이면 False
        return result['exists'] if result else False