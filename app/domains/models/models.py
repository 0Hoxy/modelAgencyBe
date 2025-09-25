"""
모델(인물) 관련 SQLAlchemy 모델
"""

from sqlalchemy import Column, String, Boolean, Date, Enum, Double
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid

from app.domains.models import model_enum


# 모델 엔티티
class Model(Base):
    """사용자 (관리자, 클라이언트) 정보"""
    __tablename__ = "models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, comment="고유 식별자")
    name = Column(String(100),nullable=False, comment="실명")  # 외국인 긴 이름 고려 (예: Maria Elena Rodriguez Garcia)
    stage_name = Column(String(100), comment="예명/활동명")  # 긴 예명 가능
    birth_date = Column(Date, nullable=False, comment="생년월일 (YYYYMMDD)")  # 20240101 형식
    gender = Column(Enum(model_enum.GenderEnum), comment="성별")
    phone = Column(String(15), nullable=False, comment="연락처 (하이픈 없음)")  # 01012345678 (최대 15자리)
    nationality = Column(String(50), comment="국적")
    has_agency = Column(Boolean, comment="소속사 여부")
    agency_name = Column(String(100), comment="소속사명")  # 회사명 길이 고려
    agency_manager_name = Column(String(50), comment="소속사 담당자명")  # 담당자 이름
    agency_manager_phone = Column(String(15), comment="소속사 담당자 연락처")  # 하이픈 없는 번호
    instagram = Column(String(100), comment="인스타그램 계정")  # 인스타그램 계정명
    tictok = Column(String(100), comment="틱톡 계정")  # 틱톡 계정명
    kakaotalk = Column(String(100), comment="카카오톡 계정") # 카카오톡 ID
    youtube = Column(String(100), comment="유튜브 채널")  # 채널명
    address_city = Column(String(30), comment="시/도 (서울특별시)")  # 시도명
    address_district = Column(String(30), comment="구/군 (강남구)")  # 구군명
    address_street = Column(String(100), comment="도로명 (테헤란로 14길 6)")  # 상세 주소
    special_abilities = Column(String(200), comment="특기/재능")  # 여러 특기 나열 가능
    first_language = Column(String(30), comment="모국어")  # 언어명
    other_language = Column(String(100), comment="구사 가능 언어")  # 여러 언어 나열
    has_tattoo = Column(Boolean, comment="타투 여부")
    tattoo_location = Column(String(100), comment="타투 위치")  # 여러 부위 설명
    tattoo_size = Column(String(20), comment="타투 크기")  # 작음/중간/큼 또는 구체적 크기
    visa_type = Column(Enum(model_enum.VisaTypeEnum), comment="비자 타입")
    height = Column(Double, nullable=False, comment="키(cm)")
    weight = Column(Double, comment="몸무게(kg)")
    top_size = Column(String(10), comment="상의 사이즈")  # XS, S, M, L, XL, XXL
    bottom_size = Column(String(10), comment="하의 사이즈")  # 28, 30, 32 등
    shoes_size = Column(String(10), comment="신발 사이즈")  # 250, 255, 260 등
    agree_term = Column(Boolean, comment="약관 동의 여부")
