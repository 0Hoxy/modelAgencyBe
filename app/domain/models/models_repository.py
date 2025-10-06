from datetime import date
from typing import Optional, List
import asyncpg

from app.core.base_repository import BaseRepository
from app.core.db import db


class ModelsRepository(BaseRepository):
    """모델 Repository"""
    def __init__(self):
        super().__init__("models")

    async def get_all_models_of_domestic(self) -> Optional[List[asyncpg.Record]]:
        query = (
            f"SELECT id, name, stage_name, birth_date, gender, phone, nationality, "
            f"agency_name, agency_manager_name, agency_manager_phone, "
            f"instagram, tictok, youtube, address_city, address_district, address_street, "
            f"special_abilities, other_languages, has_tattoo, tattoo_location, tattoo_size, "
            f"height, weight, top_size, bottom_size, shoes_size "
            f"FROM {self.table_name} WHERE is_foreigner = false"
        )
        return await db.fetch(query)

    async def get_all_models_of_foreign(self) -> Optional[List[asyncpg.Record]]:
        query = (
            f"SELECT id, name, stage_name, birth_date, gender, phone, nationality, "
            f"instagram, youtube, kakaotalk, address_city, address_district, address_street, "
            f"special_abilities, first_language, other_languages, korean_level, "
            f"has_tattoo, tattoo_location, tattoo_size, visa_type, "
            f"height, weight, top_size, bottom_size, shoes_size "
            f"FROM {self.table_name} WHERE is_foreigner = true"
        )
        return await db.fetch(query)


    async def get_models_physical_size(self, model_id: str) -> Optional[asyncpg.Record]:
        """특정 모델의 신체 사이즈 조회"""
        query = (
            f"SELECT height, weight, top_size, bottom_size, shoes_size "
            f"FROM {self.table_name} "
            f"WHERE id = $1"
        )
        return await db.fetchrow(query, model_id)

    async def get_domestic_model_by_info(self, name: str, phone: str, birth: date) -> Optional[asyncpg.Record]:
        """이름, 전화번호, 생년월일로 국내 모델 조회"""
        query = (
            f"SELECT id, name, stage_name, birth_date, gender, phone, nationality, "
            f"agency_name, agency_manager_name, agency_manager_phone, "
            f"instagram, tictok, youtube, address_city, address_district, address_street, "
            f"special_abilities, other_languages, has_agency, has_tattoo, tattoo_location, tattoo_size, "
            f"height, weight, top_size, bottom_size, shoes_size "
            f"FROM {self.table_name} "
            f"WHERE name = $1 AND phone = $2 AND birth_date = $3 AND is_foreigner = false"
        )
        return await db.fetchrow(query, name, phone, birth)

    async def get_foreign_model_by_info(self, name: str, phone: str, birth: date) -> Optional[asyncpg.Record]:
        """이름, 전화번호, 생년월일로 해외 모델 조회"""
        query = (
            f"SELECT id, name, stage_name, birth_date, gender, phone, nationality, "
            f"instagram, youtube, kakaotalk, address_city, address_district, address_street, "
            f"special_abilities, first_language, other_languages, korean_level, "
            f"has_tattoo, tattoo_location, tattoo_size, visa_type, "
            f"height, weight, top_size, bottom_size, shoes_size "
            f"FROM {self.table_name} "
            f"WHERE name = $1 AND phone = $2 AND birth_date = $3 AND is_foreigner = true"
        )
        return await db.fetchrow(query, name, phone, birth)

models_repository = ModelsRepository()