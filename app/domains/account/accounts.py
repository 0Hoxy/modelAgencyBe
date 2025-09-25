import enum
import uuid
from enum import EnumType

from pydantic import BaseModel
from sqlalchemy import Column, String, Enum, Boolean, DateTime


class Role(EnumType):
    SUPER = "SUPER"
    COMPANY = "COMPANY"
    USER = "USER"

class Account(BaseModel):

    __tablename__ = "account"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), comment="고유 식별자")
    username = Column(String)
    password = Column(String)
    email = Column(String)
    profile_img = Column(String)
    role = Column(Enum(Role))
    company_id = Column(String)
    is_active = Column(Boolean)
    is_verified = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
