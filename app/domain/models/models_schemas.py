from datetime import date
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.shared import ValidatedPhoneNumber, ValidatedPhoneNumberOptional


class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHERS = "OTHERS"

class KoreanLevel(str, Enum):
    BAD = "BAD"
    NOT_BAD = "NOT_BAD"
    GOOD = "GOOD"
    VERY_GOOD = "VERY_GOOD"

class VisaType(str, Enum):
    C1 = "C1"
    C2 = "C2"
    C3 = "C3"
    C4 = "C4"
    E1 = "E1"
    E2 = "E2"
    E3 = "E3"
    E4 = "E4"
    E5 = "E5"
    E6 = "E6"
    E7 = "E7"
    E8 = "E8"
    E9 = "E9"
    E10 = "E10"
    F1 = "F1"
    F2 = "F2"
    F3 = "F3"
    F4 = "F4"
    F5 = "F5"
    F6 = "F6"
    H1 = "H1"
    H2 = "H2"
    D1 = "D1"
    D2 = "D2"
    D3 = "D3"
    D4 = "D4"
    D5 = "D5"
    D6 = "D6"
    D7 = "D7"
    D8 = "D8"
    D9 = "D9"
    D10 = "D10"
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"
    B1 = "B1"
    B2 = "B2"

class ModelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    stage_name: str | None = Field(None, max_length=100)
    birth_date: date = Field(...)
    gender: Gender = Field(...)
    phone: ValidatedPhoneNumber = Field(...)
    nationality: str | None = Field(max_length=50)
    instagram: str | None = Field(None, max_length=100)
    youtube: str | None = Field(None, max_length=100)
    address_city: str | None = Field(max_length=50)
    address_district: str | None = Field(max_length=50)
    address_street: str | None = Field(max_length=200)
    special_abilities: str | None = Field(None, max_length=500)
    other_languages: str | None = Field(None, max_length=200)
    has_tattoo: bool = Field(default=False)
    tattoo_location: str | None = Field(None, max_length=100)
    tattoo_size: str | None = Field(None, max_length=50)
    height: float = Field(..., gt=0, le=300)  # cm 단위
    weight: float | None = Field(None, gt=0, le=500)  # kg 단위
    top_size: str | None = Field(None, max_length=10)
    bottom_size: str | None = Field(None, max_length=10)
    shoes_size: str | None = Field(None, max_length=10)
    is_foreigner: bool = Field(...)

    @model_validator(mode='after')
    def _validate_tattoo_info(self):
        if self.has_tattoo and (not self.tattoo_location or not self.tattoo_size):
            raise ValueError('타투가 있는 경우 위치, 크기 정보는 필수입니다.')
        return self

class CreateDomesticModel(ModelBase):
    has_agency: bool = Field(default=False)
    #has_agency가 True일 경우 agency_name은 필수로 들어가야 함
    agency_name: str | None = Field(None, max_length=100)
    agency_manager_name: str | None = Field(None, max_length=100)
    agency_manager_phone: ValidatedPhoneNumberOptional = Field(None)
    tiktok: str | None = Field(None, max_length=100)

    @model_validator(mode='after')
    def _validate_agency(self):
        if self.has_agency and not self.agency_name:
            raise ValueError('소속사가 있는 경우 소속사명은 필수입니다.')
        if self.agency_manager_name and len(self.agency_manager_name) not in (1, 2, 3):
            raise ValueError('담당자 이름은 1~3글자 이어야합니다.')
        return self

class CreateGlobalModel(ModelBase):
    kakaotalk: str | None = Field(None, max_length=100)
    first_language: str | None = Field(None, max_length=50)
    korean_level: KoreanLevel = Field(...)
    visa_type: VisaType = Field(...)

class ReadDomesticModel(CreateDomesticModel):
    id: UUID = Field(...)


class ReadGlobalModel(CreateGlobalModel):
    id: UUID = Field(...)

class UpdateDomesticModel(BaseModel):
    id: UUID = Field(...)
    name: str | None = Field(None, min_length=1, max_length=100)
    stage_name: str | None = Field(None, max_length=100)
    birth_date: date | None = None
    gender: Gender | None = None
    phone: ValidatedPhoneNumberOptional = Field(None)
    nationality: str | None = Field(None, max_length=50)
    instagram: str | None = Field(None, max_length=100)
    youtube: str | None = Field(None, max_length=100)
    address_city: str | None = Field(None, max_length=50)
    address_district: str | None = Field(None, max_length=50)
    address_street: str | None = Field(None, max_length=200)
    special_abilities: str | None = Field(None, max_length=500)
    other_languages: str | None = Field(None, max_length=200)
    has_tattoo: bool | None = None
    tattoo_location: str | None = Field(None, max_length=100)
    tattoo_size: str | None = Field(None, max_length=50)
    height: float | None = Field(None, gt=0, le=300)
    weight: float | None = Field(None, gt=0, le=500)
    top_size: str | None = Field(None, max_length=10)
    bottom_size: str | None = Field(None, max_length=10)
    shoes_size: str | None = Field(None, max_length=10)
    is_foreigner: bool | None = None
    has_agency: bool | None = None
    agency_name: str | None = Field(None, max_length=100)
    agency_manager_name: str | None = Field(None, max_length=100)
    agency_manager_phone: ValidatedPhoneNumberOptional = Field(None)
    tiktok: str | None = Field(None, max_length=100)


class UpdateGlobalModel(BaseModel):
    id: UUID = Field(...)
    name: str | None = Field(None, min_length=1, max_length=100)
    stage_name: str | None = Field(None, max_length=100)
    birth_date: date | None = None
    gender: Gender | None = None
    phone: ValidatedPhoneNumberOptional = Field(None)
    nationality: str | None = Field(None, max_length=50)
    instagram: str | None = Field(None, max_length=100)
    youtube: str | None = Field(None, max_length=100)
    address_city: str | None = Field(None, max_length=50)
    address_district: str | None = Field(None, max_length=50)
    address_street: str | None = Field(None, max_length=200)
    special_abilities: str | None = Field(None, max_length=500)
    other_languages: str | None = Field(None, max_length=200)
    has_tattoo: bool | None = None
    tattoo_location: str | None = Field(None, max_length=100)
    tattoo_size: str | None = Field(None, max_length=50)
    height: float | None = Field(None, gt=0, le=300)
    weight: float | None = Field(None, gt=0, le=500)
    top_size: str | None = Field(None, max_length=10)
    bottom_size: str | None = Field(None, max_length=10)
    shoes_size: str | None = Field(None, max_length=10)
    is_foreigner: bool | None = None
    kakaotalk: str | None = Field(None, max_length=100)
    first_language: str | None = Field(None, max_length=50)
    korean_level: KoreanLevel | None = None
    visa_type: VisaType | None = None

class DeleteModel(BaseModel):
    id: UUID = Field(...)


class ModelResponse(BaseModel):
    name: str = Field(...)
    message : str = Field(...)

class ReadRevisitedModel(BaseModel):
    name: str = Field(...)
    phone: str = Field(...)
    birth: date = Field(...)

class GetModelId(BaseModel):
    id: UUID = Field(...)