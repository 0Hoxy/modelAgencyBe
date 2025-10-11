from typing import Optional, List, Awaitable
from contextlib import asynccontextmanager

import asyncpg

from app.core.config import settings

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self) -> None:
        """데이터베이스 연결 풀 생성"""
        pool_creation: Awaitable[asyncpg.Pool] = asyncpg.create_pool(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            min_size=5,
            max_size=20,
            timeout=30
        )
        self.pool = await pool_creation

        assert self.pool is not None

    async def disconnect(self):
        """데이터베이스 연결 풀 종료"""
        if self.pool:
            await self.pool.close()

    async def execute(self, query: str, *args) -> None :
        """쿼리 실행"""
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> List[asyncpg.Record] :
        """쿼리 결과 조회"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> asyncpg.Record:
        """단일 행 조회"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchmany(self, query: str, *args) -> List[asyncpg.Record] :
        """특정 개수 행 조회"""
        async with self.pool.acquire() as conn:
            return await conn.fetchmany(query, *args)

    async def fetchval(self, query: str, *args):
        """단일 값 조회 (첫 번째 컬럼의 첫 번째 행)"""
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    @asynccontextmanager
    async def transaction(self):
        """트랜잭션 컨텍스트 매니저"""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                yield conn

    async def execute_transaction(self, conn: asyncpg.Connection, query: str, *args):
        """트랜잭션 내에서 쿼리 실행"""
        return await conn.execute(query, *args)

    async def fetchrow_transaction(self, conn: asyncpg.Connection, query: str, *args):
        """트랜잭션 내에서 단일 행 조회"""
        return await conn.fetchrow(query, *args)

    async def fetch_transaction(self, conn: asyncpg.Connection, query: str, *args):
        """트랜잭션 내에서 여러 행 조회"""
        return await conn.fetch(query, *args)

db = Database()
