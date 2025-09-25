"""
모델(인물) 관련 Pydantic 스키마
"""
import uuid
from datetime import date
from typing import Optional

from phonenumbers import PhoneNumber
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from .model_enum import (GenderEnum, VisaTypeEnum)

# --- 유효성 검사기 ---
class SizeValidatorMixin:
    @field_validator('top_size', 'bottom_size', 'shoes_size', check_fields=False)
    @classmethod
    def validate_size_is_positive(cls, value):
        if isinstance(value, int) and value <= 0:
            raise ValueError('사이즈는 0보다 커야 합니다.')
        return value

class ConditionalLogicMixin:
    @model_validator(mode='after')
    def validate_conditional_logic(self):
        if getattr(self, 'has_tattoo', False) and not getattr(self, 'tattoo_location', None):
            raise ValueError("타투가 있는 경우, 타투 위치는 필수입니다.")
        if getattr(self, 'has_agency', False) and not getattr(self, 'agency_name', None):
            raise ValueError("소속사가 있을 경우 소속사명은 필수입니다.")
        return self

class OrmConfigMixin:
    """ORM 객체와의 호환을 위한 Pydantic Config 믹스인"""
    class Config:
        from_attributes = True

# --- Base 및 Create 스키마 ---
class ModelBase(BaseModel, SizeValidatorMixin):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(...)
    stage_name: str | None = Field(default=None)
    birth_date: date = Field(...)
    gender: GenderEnum = Field(...)
    phone: PhoneNumber = Field(...)
    nationality: str | None = Field(default=None)
    instagram: str | None = Field(default=None)
    youtube: str | None = Field(default=None)
    address_city: str | None = Field(default=None)
    address_district: str | None = Field(default=None)
    address_street: str | None = Field(default=None)
    special_abilities: str | None = Field(default=None)
    other_languages: str | None = Field(default=None)
    has_tattoo: bool = Field(default=False)
    tattoo_location: str | None = Field(default=None)
    tattoo_size: str | None = Field(default=None)
    height: float = Field(..., gt=0)
    weight: float | None = Field(default=None, gt=0)
    top_size: str | int | None = Field(default=None)
    bottom_size: str | int | None = Field(default=None)
    shoes_size: str | int | None = Field(default=None)
    agree_term: bool = Field(...)

class CreateDomesticModel(ModelBase, ConditionalLogicMixin):
    has_agency: bool = Field(default=False)
    agency_name: str | None = Field(default=None)
    agency_manager_name: str | None = Field(default=None)
    agency_manager_phone: PhoneNumber | None = Field(default=None)
    tictok : str | None = Field(default=None)

class CreateOverseaModel(ModelBase, ConditionalLogicMixin):
    kakaotalk: str | None = Field(default=None)
    first_language: str | None = Field(default=None)
    visa_type: VisaTypeEnum | None = Field(default=None)

# --- Update 스키마 (명시적 클래스 정의) ---
class UpdateModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # 기본 정보
    name: str | None = Field(default=None)
    stage_name: str | None = Field(default=None)
    birth_date: date | None = Field(default=None)
    gender: GenderEnum | None = Field(default=None)
    phone: PhoneNumber | None = Field(default=None)
    nationality: str | None = Field(default=None)

    # 소속사 정보
    has_agency: bool | None = Field(default=None)
    agency_name: str | None = Field(default=None)
    agency_manager_name: str | None = Field(default=None)
    agency_manager_phone: PhoneNumber | None = Field(default=None)

    # SNS 계정
    instagram: str | None = Field(default=None)
    tictok: str | None = Field(default=None)
    kakaotalk: str | None = Field(default=None)
    youtube: str | None = Field(default=None)

    # 주소 정보
    address_city: str | None = Field(default=None)
    address_district: str | None = Field(default=None)
    address_street: str | None = Field(default=None)

    # 기타 정보
    special_abilities: str | None = Field(default=None)
    first_language: str | None = Field(default=None)
    other_language: str | None = Field(default=None)

    # 타투 정보
    has_tattoo: bool | None = Field(default=None)
    tattoo_location: str | None = Field(default=None)
    tattoo_size: str | None = Field(default=None)

    # 비자 및 신체 정보
    visa_type: VisaTypeEnum | None = Field(default=None)
    height: float | None = Field(default=None)
    weight: float | None = Field(default=None)

    # 사이즈 정보
    top_size: str | None = Field(default=None)
    bottom_size: str | None = Field(default=None)
    shoes_size: str | None = Field(default=None)

    # 약관 동의
    agree_term: bool | None = Field(default=None)

# --- Read 스키마 (변경 없음) ---
class ReadBase(BaseModel, OrmConfigMixin):
    id: uuid.UUID

class ReadDomesticModel(CreateDomesticModel, ReadBase):
    pass

class ReadOverseaModel(CreateOverseaModel, ReadBase):
    pass

class CreateModelResponse(BaseModel, OrmConfigMixin):
    name: str
    message: str = "님의 접수가 완료되었습니다."