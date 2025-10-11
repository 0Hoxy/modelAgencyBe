"""
관리자 도메인 Repository
- 모델 검색
- 카메라 테스트 관리
- 대시보드 통계
"""
from typing import Optional, List
from datetime import date, datetime, timedelta
from uuid import UUID

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
        
        # 국적 검색
        if search_params.nationality:
            conditions.append(f"nationality ILIKE ${param_index}")
            params.append(f"%{search_params.nationality}%")
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
        
        # 주소 (동) 검색
        if search_params.address_street:
            conditions.append(f"address_street ILIKE ${param_index}")
            params.append(f"%{search_params.address_street}%")
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
                instagram, youtube, {f"kakaotalk," if is_foreigner else "tictok,"}
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
    
    async def get_physical_size(self, model_id: UUID) -> Optional[asyncpg.Record]:
        """모델 신체 사이즈 조회"""
        query = f"""
            SELECT id as model_id, name, height, weight, top_size, bottom_size, shoes_size
            FROM {self.table_name}
            WHERE id = $1
        """
        return await db.fetchrow(query, model_id)

    # ===== 카메라 테스트 관리 =====
    
    async def get_camera_test(self, model_id: UUID) -> Optional[asyncpg.Record]:
        """카메라 테스트 조회"""
        query = """
            SELECT id, model_id, is_tested, visited_at
            FROM cameratest
            WHERE model_id = $1
            ORDER BY visited_at DESC
            LIMIT 1
        """
        return await db.fetchrow(query, model_id)

    async def get_camera_test_today(self, model_id: UUID) -> Optional[asyncpg.Record]:
        """금일 카메라 테스트 조회"""
        query = """
            SELECT id, model_id, is_tested, visited_at
            FROM cameratest
            WHERE model_id = $1
            AND visited_at >= CURRENT_DATE
            AND visited_at < CURRENT_DATE + INTERVAL '1 day'
            ORDER BY visited_at DESC
            LIMIT 1
        """
        return await db.fetchrow(query, model_id)
    
    async def create_camera_test_transaction(
        self,
        conn: asyncpg.Connection,
        model_id: UUID,
        visited_at: datetime
    ) -> asyncpg.Record:
        """카메라 테스트 등록 (트랜잭션)"""
        query = """
            INSERT INTO cameratest (model_id, is_tested, visited_at)
            VALUES ($1, $2::camerateststatusenum, $3)
            RETURNING id, model_id, is_tested, visited_at
        """
        return await conn.fetchrow(query, model_id, 'PENDING', visited_at)
    
    async def update_camera_test_status_transaction(
        self,
        conn: asyncpg.Connection,
        model_id: UUID,
        status: CameraTestStatus
    ) -> Optional[asyncpg.Record]:
        """카메라 테스트 상태 변경 (트랜잭션)"""
        query = """
            UPDATE cameratest
            SET is_tested = $2::camerateststatusenum
            WHERE model_id = $1
            RETURNING id, model_id, is_tested, visited_at
        """
        return await conn.fetchrow(query, model_id, status.value)

    # ===== 대시보드 통계 =====
    
    async def get_daily_registrations(
        self,
        start_date: date,
        end_date: date
    ) -> List[asyncpg.Record]:
        """일별 등록 인원 통계 (중복 제거: 같은 model_id는 1명으로 카운트)"""
        query = """
            SELECT
                DATE(visited_at) as date,
                COUNT(DISTINCT model_id) as count
            FROM cameratest
            WHERE DATE(visited_at) BETWEEN $1 AND $2
            GROUP BY DATE(visited_at)
            ORDER BY date DESC
        """
        return await db.fetch(query, start_date, end_date)

    async def get_cameratests_by_date(self, target_date: date) -> List[asyncpg.Record]:
        """특정 날짜의 카메라테스트 + 모델 정보

        - 같은 model_id는 한 번만 반환 (해당 날짜의 가장 이른 방문시간)
        - 정렬: cameratest.visited_at 오름차순
        - 반환 컬럼: 모델(name, birth_date, nationality, height, agency_name, visa_type),
                    cameratest(is_tested, visited_at, id as cameratest_id, model_id)
        """
        query = """
            SELECT
                ct.id               AS id,
                ct.model_id         AS model_id,
                ct.is_tested        AS is_tested,
                ct.visited_at       AS visited_at,
                m.name              AS name,
                m.birth_date        AS birth_date,
                m.nationality       AS nationality,
                m.height            AS height,
                m.agency_name       AS agency_name,
                m.visa_type         AS visa_type
            FROM (
                SELECT DISTINCT ON (model_id)
                    id, model_id, is_tested, visited_at
                FROM cameratest
                WHERE DATE(visited_at) = $1
                ORDER BY model_id, visited_at ASC
            ) ct
            INNER JOIN models m ON m.id = ct.model_id
            ORDER BY ct.visited_at ASC
        """
        return await db.fetch(query, target_date)
    
    async def get_today_registrations_count(self) -> int:
        """금일 등록 인원 수 (중복 제거: 같은 model_id는 1명으로 카운트)"""
        query = """
            SELECT COUNT(DISTINCT model_id) as count
            FROM cameratest
            WHERE DATE(visited_at) = CURRENT_DATE
        """
        result = await db.fetchrow(query)
        return result["count"] if result else 0
    
    async def get_today_incomplete_camera_tests_count(self) -> int:
        """금일 카메라테스트 미완료 인원 (중복 제거: 완료가 아닌 상태의 고유 model_id 수)"""
        query = """
            SELECT COUNT(DISTINCT model_id) as count
            FROM cameratest
            WHERE DATE(visited_at) = CURRENT_DATE AND is_tested = 'PENDING'
        """
        result = await db.fetchrow(query)
        return result["count"] if result else 0
    
    async def get_incomplete_addresses_count(self) -> int:
        """주소록 등록 미완료 인원: 현재 테이블 미구현이므로 0 고정 반환"""
        return 0
    
    async def model_exists_transaction(self, conn: asyncpg.Connection, model_id: str) -> bool:
        """트랜잭션 내에서 모델 존재 여부 확인"""
        query = "SELECT EXISTS(SELECT 1 FROM models WHERE id = $1)"
        result = await conn.fetchval(query, model_id)
        return result
    
    async def delete_model_transaction(self, conn: asyncpg.Connection, model_id: str) -> dict | None:
        """트랜잭션 내에서 모델 삭제 (cameratest 먼저 삭제 후 models 삭제)"""
        # 1단계: cameratest 삭제 (외래키 제약 조건 해결)
        await conn.execute("DELETE FROM cameratest WHERE model_id = $1", model_id)
        
        # 2단계: models 삭제
        query = """
            DELETE FROM models
            WHERE id = $1
            RETURNING id, name
        """
        result = await conn.fetchrow(query, model_id)
        return dict(result) if result else None
    
    async def get_filter_options(self) -> dict:
        """필터 옵션들을 수집"""
        # 1. 국적 수집 (실제 DB 데이터)
        nationalities = await self.get_unique_nationalities()
        
        # 2. 특기 수집 (실제 DB 데이터)
        specialties = await self.get_unique_specialties()
        
        # 3. 언어 수집 (실제 DB 데이터)
        languages = await self.get_unique_languages()
        
        # 4. 한국어 수준 (enum 하드코딩)
        korean_levels = self.get_korean_level_options()
        
        # 5. 비자 타입 (enum 하드코딩)
        visa_types = self.get_visa_type_options()
        
        # 6. 주소 시/도 수집 (실제 DB 데이터)
        address_cities = await self.get_unique_address_cities()
        
        return {
            "nationalities": nationalities,
            "specialties": specialties,
            "languages": languages,
            "korean_levels": korean_levels,
            "visa_types": visa_types,
            "address_cities": address_cities,
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "version": "1.0.0",
                "total_counts": {
                    "nationalities": len(nationalities),
                    "specialties": len(specialties),
                    "languages": len(languages),
                    "korean_levels": len(korean_levels),
                    "visa_types": len(visa_types),
                    "address_cities": len(address_cities)
                }
            }
        }
    
    async def get_unique_nationalities(self) -> List[dict]:
        """국적 목록 수집"""
        query = """
            SELECT DISTINCT nationality as value
            FROM models 
            WHERE nationality IS NOT NULL AND nationality != ''
            ORDER BY nationality
        """
        results = await db.fetch(query)
        return [{"label": row["value"], "value": row["value"]} for row in results]
    
    async def get_unique_specialties(self) -> List[dict]:
        """특기 목록 수집 (special_abilities에서 파싱)"""
        query = """
            SELECT DISTINCT TRIM(unnest(string_to_array(special_abilities, ','))) as value
            FROM models 
            WHERE special_abilities IS NOT NULL AND special_abilities != ''
            ORDER BY value
        """
        results = await db.fetch(query)
        return [{"label": row["value"], "value": row["value"]} for row in results]
    
    async def get_unique_languages(self) -> List[dict]:
        """언어 목록 수집 (other_languages에서 파싱)"""
        query = """
            SELECT DISTINCT TRIM(unnest(string_to_array(other_languages, ','))) as value
            FROM models 
            WHERE other_languages IS NOT NULL AND other_languages != ''
            ORDER BY value
        """
        results = await db.fetch(query)
        return [{"label": row["value"], "value": row["value"]} for row in results]
    
    def get_korean_level_options(self) -> List[dict]:
        """한국어 수준 옵션 (enum 하드코딩)"""
        return [
            {"label": "초급", "value": "BAD", "description": "기초적인 한국어만 가능"},
            {"label": "중급", "value": "NOT_BAD", "description": "일상 대화 가능"},
            {"label": "고급", "value": "GOOD", "description": "비즈니스 대화 가능"},
            {"label": "원어민 수준", "value": "VERY_GOOD", "description": "원어민 수준"}
        ]
    
    def get_visa_type_options(self) -> List[dict]:
        """비자 타입 옵션 (enum 하드코딩)"""
        return [
            {"label": "E-1 (교수)", "value": "E-1", "description": "대학에서 강의하는 교수"},
            {"label": "E-2 (회화지도)", "value": "E-2", "description": "외국어 회화지도"},
            {"label": "E-3 (연구)", "value": "E-3", "description": "연구 활동"},
            {"label": "E-4 (기술지도)", "value": "E-4", "description": "기술 지도"},
            {"label": "E-5 (전문직)", "value": "E-5", "description": "전문직 업무"},
            {"label": "E-6 (예술흥행)", "value": "E-6", "description": "예술 및 흥행 활동"},
            {"label": "E-7 (특정활동)", "value": "E-7", "description": "특정 활동"},
            {"label": "F-1 (방문동거)", "value": "F-1", "description": "방문 동거"},
            {"label": "F-2 (거주)", "value": "F-2", "description": "거주"},
            {"label": "F-4 (재외동포)", "value": "F-4", "description": "재외동포"},
            {"label": "F-5 (영주)", "value": "F-5", "description": "영주"},
            {"label": "F-6 (결혼이민)", "value": "F-6", "description": "결혼이민"},
            {"label": "H-1 (관광취업)", "value": "H-1", "description": "관광취업"},
            {"label": "H-2 (방문취업)", "value": "H-2", "description": "방문취업"},
            {"label": "기타", "value": "OTHER", "description": "기타 비자"}
        ]
    
    async def get_unique_address_cities(self) -> List[dict]:
        """주소 시/도 목록 수집 (구/군, 동 포함)"""
        query = """
            SELECT DISTINCT address_city as value
            FROM models 
            WHERE address_city IS NOT NULL AND address_city != ''
            ORDER BY address_city
        """
        results = await db.fetch(query)
        
        address_cities = []
        for row in results:
            city = row["value"]
            districts = await self.get_districts_by_city(city)
            address_cities.append({
                "label": city,
                "value": city,
                "districts": districts
            })
        
        return address_cities
    
    async def get_districts_by_city(self, city: str) -> List[dict]:
        """특정 시/도의 구/군 목록 수집 (동 포함)"""
        query = """
            SELECT DISTINCT address_district
            FROM models 
            WHERE address_city = $1 AND address_district IS NOT NULL AND address_district != ''
            ORDER BY address_district
        """
        results = await db.fetch(query, city)
        
        districts = []
        for row in results:
            district = row["address_district"]
            dongs = await self.get_dongs_by_district(city, district)
            districts.append({
                "label": district,
                "value": district,
                "dongs": dongs
            })
        
        return districts
    
    async def get_dongs_by_district(self, city: str, district: str) -> List[str]:
        """특정 구/군의 동 목록 수집"""
        query = """
            SELECT DISTINCT address_street
            FROM models 
            WHERE address_city = $1 AND address_district = $2 
            AND address_street IS NOT NULL AND address_street != ''
            ORDER BY address_street
        """
        results = await db.fetch(query, city, district)
        return [row["address_street"] for row in results]


# Singleton 인스턴스
admins_repository = AdminsRepository()
