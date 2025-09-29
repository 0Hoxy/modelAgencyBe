from typing import Optional, List, Awaitable

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

db = Database()
