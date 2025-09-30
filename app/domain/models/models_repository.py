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
            f"SELECT id, name, stage_name, birth_date, gender, phone, nationality, agency_name, agency_manager_name, agency_manager_phone,"
            f"instagram, tictok, youtube, address_city, address_district, address_street, special_abilities, other_language, tattoo_location,"
            f"tattoo_size "
            f"FROM {self.table_name} WHERE is_foreigner = false")
        return await db.fetch(query)

    async def get_all_models_of_foreign(self) -> Optional[List[asyncpg.Record]]:
        query = (
            f"SELECT id, name, stage_name, birth_date, gender, phone, nationality, instagram, youtube, kakaotalk, "
            f"address_city, address_district, address_street, special_abilities, first_language, other_language, tattoo_location, "
            f"tattoo_size, visa_type "
            f"FROM {self.table_name} "
            f"WHERE is_foreigner = true")
        return await db.fetch(query)


    async def get_models_physical_size(self) -> Optional[asyncpg.Record]:
        query = (
            f"SELECT height, weight, top_size, bottom_size, shoes_size "
            f"FROM {self.table_name} "
            f"WHERE id")
        return await db.fetchrow(query)

    async def get_domestic_model_by_info(self, name: str, phone: str, birth: date) -> asyncpg.Record:
        query = (
            f"SELECT id, name, stage_name, birth_date, gender, phone, nationality, agency_name, agency_manager_name, agency_manager_phone,"
                 f"instagram, tictok, youtube, address_city, address_district, address_street, special_abilities, other_language, tattoo_location,"
                 f"tattoo_size "
            f"FROM {self.table_name} "
            f"WHERE name={name}, phone={phone}, birth_date={birth}, is_foreigner=false")

        return await db.fetchrow(query)

    async def get_foreign_model_by_info(self, name: str, phone: str, birth: date) -> asyncpg.Record:
        query = (
            f"SELECT id, name, stage_name, birth_date, gender, phone, nationality, instagram, youtube, kakaotalk, "
            f"address_city, address_district, address_street, special_abilities, first_language, other_language, tattoo_location, "
            f"tattoo_size, visa_type "
            f"FROM {self.table_name} "
            f"WHERE name={name}, phone={phone}, birth_date={birth}, is_foreigner=false")

        return await db.fetchrow(query)

models_repository = ModelsRepository()