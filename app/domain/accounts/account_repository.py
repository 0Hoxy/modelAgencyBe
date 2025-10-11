from typing import Optional
import asyncpg

from app.core.base_repository import BaseRepository
from app.core.db import db


class AccountRepository(BaseRepository):
    """계정 Repository"""
    
    def __init__(self):
        super().__init__("admins")

    async def get_by_pid(self, pid: str) -> Optional[asyncpg.Record]:
        """
        이메일(pid)로 사용자 조회
        
        Args:
            pid: 이메일 (고유 식별자)
            
        Returns:
            asyncpg.Record: 사용자 정보 (없으면 None)
        """
        query = f"""
            SELECT admin_id as id, name, pid, password, role, provider, provider_id, created_at
            FROM {self.table_name}
            WHERE pid = $1
        """
        return await db.fetchrow(query, pid)

    async def check_pid_exists(self, pid: str) -> bool:
        """
        이메일(pid) 중복 확인
        
        Args:
            pid: 이메일
            
        Returns:
            bool: 중복 여부 (True: 중복됨, False: 사용 가능)
        """
        query = f"""
            SELECT EXISTS(SELECT 1 FROM {self.table_name} WHERE pid = $1)
        """
        result = await db.fetchrow(query, pid)
        return result['exists'] if result else False
    
    async def verify_password(self, pid: str, password: str) -> bool:
        """
        비밀번호 검증
        
        Args:
            pid: 이메일
            password: 검증할 비밀번호
            
        Returns:
            bool: 비밀번호 일치 여부
        """
        user = await self.get_by_pid(pid)
        if not user:
            return False
        
        # bcrypt를 사용하여 비밀번호 검증
        import bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8'))
    
    async def change_password_with_transaction(self, pid: str, new_password: str) -> None:
        """
        비밀번호 변경 (평문 비밀번호를 받아서 해시화 후 트랜잭션 처리)
        
        Args:
            pid: 이메일
            new_password: 새로운 비밀번호 (평문)
        """
        import bcrypt
        
        # 새 비밀번호 해시화
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
        
        # 트랜잭션으로 비밀번호 업데이트
        async with db.transaction() as conn:
            await self.update_password_transaction(conn, pid, password_hash)
    

    async def create_account_transaction(
        self,
        conn: asyncpg.Connection,
        data: dict
    ) -> Optional[asyncpg.Record]:
        """
        트랜잭션 내에서 계정 생성
        
        Args:
            conn: 트랜잭션 연결 객체
            data: 계정 데이터
            
        Returns:
            asyncpg.Record: 생성된 계정 정보 (password 제외)
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(f"${i + 1}" for i in range(len(data)))
        
        query = f"""
            INSERT INTO {self.table_name} ({columns})
            VALUES ({placeholders})
            RETURNING admin_id as id, name, pid, role, provider, provider_id, created_at
        """
        return await conn.fetchrow(query, *data.values())

    async def update_password_transaction(
        self,
        conn: asyncpg.Connection,
        pid: str,
        new_password_hash: str
    ) -> Optional[asyncpg.Record]:
        """
        트랜잭션 내에서 비밀번호 변경
        
        Args:
            conn: 트랜잭션 연결 객체
            pid: 이메일
            new_password_hash: 새로운 비밀번호 해시
            
        Returns:
            asyncpg.Record: 업데이트된 계정 정보
        """
        query = f"""
            UPDATE {self.table_name}
            SET password = $2
            WHERE pid = $1
            RETURNING admin_id as id, name, pid, role, provider, created_at
        """
        return await conn.fetchrow(query, pid, new_password_hash)

    async def delete_by_id_transaction(
        self,
        conn: asyncpg.Connection,
        account_id: str
    ) -> Optional[asyncpg.Record]:
        """
        트랜잭션 내에서 계정 삭제
        
        Args:
            conn: 트랜잭션 연결 객체
            account_id: 계정 ID
            
        Returns:
            asyncpg.Record: 삭제된 계정 정보
        """
        query = f"""
            DELETE FROM {self.table_name}
            WHERE admin_id = $1
            RETURNING admin_id as id, name, pid, role
        """
        return await conn.fetchrow(query, account_id)


account_repository = AccountRepository()
