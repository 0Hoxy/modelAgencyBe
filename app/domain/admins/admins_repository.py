"""
관리자 도메인 Repository
- 모델 검색
- 카메라 테스트 관리
- 대시보드 통계
"""
from typing import Optional, List
from datetime import date, datetime, timedelta
import asyncpg

from app.core.base_repository import BaseRepository
from app.core.db import db
from app.domain.admins.admins_schemas import ModelSearchParams, CameraTestStatus


class AdminsRepository(BaseRepository):
    """관리자 Repository"""
    
    def __init__(self):
        super().__init__("models")

    # ===== 모델 검색 =====
    
    async def search_models(
        self,
        search_params: ModelSearchParams,
        is_foreigner: bool
    ) -> List[asyncpg.Record]:
        """
        모델 검색 (필터링)
        
        Args:
            search_params: 검색 조건
            is_foreigner: True=해외모델, False=국내모델
        """
        conditions = ["is_foreigner = $1"]
        params = [is_foreigner]
        param_index = 2
        
        # 이름 검색 (부분 일치)
        if search_params.name:
            conditions.append(f"name ILIKE ${param_index}")
            params.append(f"%{search_params.name}%")
            param_index += 1
        
        # 성별 검색
        if search_params.gender:
            conditions.append(f"gender = ${param_index}")
            params.append(search_params.gender)
            param_index += 1
        
        # 주소 (시) 검색
        if search_params.address_city:
            conditions.append(f"address_city ILIKE ${param_index}")
            params.append(f"%{search_params.address_city}%")
            param_index += 1
        
        # 주소 (구) 검색
        if search_params.address_district:
            conditions.append(f"address_district ILIKE ${param_index}")
            params.append(f"%{search_params.address_district}%")
            param_index += 1
        
        # 특기 검색 (부분 일치)
        if search_params.special_abilities:
            conditions.append(f"special_abilities ILIKE ${param_index}")
            params.append(f"%{search_params.special_abilities}%")
            param_index += 1
        
        # 가능한 외국어 검색 (부분 일치)
        if search_params.other_languages:
            conditions.append(f"other_languages ILIKE ${param_index}")
            params.append(f"%{search_params.other_languages}%")
            param_index += 1
        
        # 한국어 수준 검색 (해외 모델만)
        if search_params.korean_level and is_foreigner:
            conditions.append(f"korean_level = ${param_index}")
            params.append(search_params.korean_level)
            param_index += 1
        
        where_clause = " AND ".join(conditions)
        
        # 페이징
        offset = (search_params.page - 1) * search_params.page_size
        limit = search_params.page_size
        
        query = f"""
            SELECT 
                id, name, stage_name, birth_date, gender, phone, nationality,
                address_city, address_district, address_street,
                special_abilities, other_languages,
                {f"korean_level, visa_type, first_language," if is_foreigner else "agency_name, agency_manager_name, agency_manager_phone,"}
                height, weight, top_size, bottom_size, shoes_size,
                has_tattoo, tattoo_location, tattoo_size,
                instagram, youtube, {f"kakaotalk," if is_foreigner else "tiktok,"}
                created_at
            FROM {self.table_name}
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ${param_index} OFFSET ${param_index + 1}
        """
        params.extend([limit, offset])
        
        return await db.fetch(query, *params)
    
    async def count_models(
        self,
        search_params: ModelSearchParams,
        is_foreigner: bool
    ) -> int:
        """모델 검색 결과 총 개수"""
        conditions = ["is_foreigner = $1"]
        params = [is_foreigner]
        param_index = 2
        
        if search_params.name:
            conditions.append(f"name ILIKE ${param_index}")
            params.append(f"%{search_params.name}%")
            param_index += 1
        
        if search_params.gender:
            conditions.append(f"gender = ${param_index}")
            params.append(search_params.gender)
            param_index += 1
        
        if search_params.address_city:
            conditions.append(f"address_city ILIKE ${param_index}")
            params.append(f"%{search_params.address_city}%")
            param_index += 1
        
        if search_params.address_district:
            conditions.append(f"address_district ILIKE ${param_index}")
            params.append(f"%{search_params.address_district}%")
            param_index += 1
        
        if search_params.special_abilities:
            conditions.append(f"special_abilities ILIKE ${param_index}")
            params.append(f"%{search_params.special_abilities}%")
            param_index += 1
        
        if search_params.other_languages:
            conditions.append(f"other_languages ILIKE ${param_index}")
            params.append(f"%{search_params.other_languages}%")
            param_index += 1
        
        if search_params.korean_level and is_foreigner:
            conditions.append(f"korean_level = ${param_index}")
            params.append(search_params.korean_level)
            param_index += 1
        
        where_clause = " AND ".join(conditions)
        
        query = f"""
            SELECT COUNT(*) as count
            FROM {self.table_name}
            WHERE {where_clause}
        """
        
        result = await db.fetchrow(query, *params)
        return result["count"] if result else 0

    # ===== 신체 사이즈 조회 =====
    
    async def get_physical_size(self, model_id: int) -> Optional[asyncpg.Record]:
        """모델 신체 사이즈 조회"""
        query = f"""
            SELECT id as model_id, name, height, weight, top_size, bottom_size, shoes_size
            FROM {self.table_name}
            WHERE id = $1
        """
        return await db.fetchrow(query, model_id)

    # ===== 카메라 테스트 관리 =====
    
    async def get_camera_test(self, model_id: int) -> Optional[asyncpg.Record]:
        """카메라 테스트 조회"""
        query = """
            SELECT id, model_id, is_tested, visited_at
            FROM cameratest
            WHERE model_id = $1
            ORDER BY visited_at DESC
            LIMIT 1
        """
        return await db.fetchrow(query, model_id)
    
    async def create_camera_test_transaction(
        self,
        conn: asyncpg.Connection,
        model_id: int,
        visited_at: datetime
    ) -> asyncpg.Record:
        """카메라 테스트 등록 (트랜잭션)"""
        query = """
            INSERT INTO cameratest (model_id, is_tested, visited_at)
            VALUES ($1, $2, $3)
            RETURNING id, model_id, is_tested, visited_at
        """
        return await conn.fetchrow(query, model_id, False, visited_at)
    
    async def update_camera_test_status_transaction(
        self,
        conn: asyncpg.Connection,
        model_id: int,
        status: CameraTestStatus
    ) -> Optional[asyncpg.Record]:
        """카메라 테스트 상태 변경 (트랜잭션)"""
        # 상태를 boolean으로 변환
        is_tested_map = {
            CameraTestStatus.READY: False,
            CameraTestStatus.TESTING: False,
            CameraTestStatus.COMPLETED: True
        }
        is_tested = is_tested_map.get(status, False)
        
        query = """
            UPDATE cameratest
            SET is_tested = $2
            WHERE model_id = $1
            RETURNING id, model_id, is_tested, visited_at
        """
        return await conn.fetchrow(query, model_id, is_tested)

    # ===== 대시보드 통계 =====
    
    async def get_daily_registrations(
        self,
        start_date: date,
        end_date: date
    ) -> List[asyncpg.Record]:
        """일별 등록 인원 통계"""
        query = f"""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as count
            FROM {self.table_name}
            WHERE DATE(created_at) BETWEEN $1 AND $2
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """
        return await db.fetch(query, start_date, end_date)
    
    async def get_today_registrations_count(self) -> int:
        """금일 등록 모델 수"""
        query = f"""
            SELECT COUNT(*) as count
            FROM {self.table_name}
            WHERE DATE(created_at) = CURRENT_DATE
        """
        result = await db.fetchrow(query)
        return result["count"] if result else 0
    
    async def get_today_incomplete_camera_tests_count(self) -> int:
        """금일 카메라테스트 미완료 인원"""
        query = """
            SELECT COUNT(*) as count
            FROM cameratest
            WHERE DATE(visited_at) = CURRENT_DATE AND is_tested = FALSE
        """
        result = await db.fetchrow(query)
        return result["count"] if result else 0
    
    async def get_incomplete_addresses_count(self) -> int:
        """주소록 등록 미완료 인원 (주소가 NULL이거나 비어있는 경우)"""
        query = f"""
            SELECT COUNT(*) as count
            FROM {self.table_name}
            WHERE address_city IS NULL 
               OR address_city = ''
               OR address_district IS NULL 
               OR address_district = ''
        """
        result = await db.fetchrow(query)
        return result["count"] if result else 0


# Singleton 인스턴스
admins_repository = AdminsRepository()
