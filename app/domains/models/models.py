"""
모델(인물) 관련 SQLAlchemy 모델
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Model(Base):
    """모델(인물) 정보"""
    __tablename__ = "models"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, comment="모델 이름")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="이메일")
    phone = Column(String(20), comment="전화번호")
    
    # 기본 정보
    age = Column(Integer, comment="나이")
    height = Column(Integer, comment="키(cm)")
    weight = Column(Integer, comment="몸무게(kg)")
    gender = Column(String(10), comment="성별")
    
    # 상세 정보
    bio = Column(Text, comment="자기소개")
    experience = Column(Text, comment="경력")
    specialties = Column(JSON, comment="전문 분야 (배열)")
    
    # 상태 정보
    is_active = Column(Boolean, default=True, comment="활성 상태")
    is_verified = Column(Boolean, default=False, comment="인증 상태")
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow, comment="생성일")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정일")

    def __repr__(self):
        return f"<Model(id={self.id}, name={self.name}, email={self.email})>"


class Portfolio(Base):
    """포트폴리오 정보"""
    __tablename__ = "portfolios"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    model_id = Column(String, nullable=False, index=True, comment="모델 ID")
    title = Column(String(200), nullable=False, comment="포트폴리오 제목")
    description = Column(Text, comment="설명")
    
    # 파일 정보
    image_urls = Column(JSON, comment="이미지 URL 목록")
    video_urls = Column(JSON, comment="비디오 URL 목록")
    
    # 분류
    category = Column(String(50), comment="카테고리")
    tags = Column(JSON, comment="태그 목록")
    
    # 상태
    is_public = Column(Boolean, default=True, comment="공개 여부")
    is_featured = Column(Boolean, default=False, comment="추천 여부")
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow, comment="생성일")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정일")

    def __repr__(self):
        return f"<Portfolio(id={self.id}, model_id={self.model_id}, title={self.title})>"
