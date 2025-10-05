"""
보안 관련 유틸리티
- 비밀번호 해싱 (bcrypt)
- JWT 토큰 생성/검증
"""
from datetime import datetime, timedelta
from typing import Optional
from app.core.config import settings
import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError


# JWT 설정 (실제 환경에서는 환경변수로 관리)
SECRET_KEY = settings.SECRET_KEY;
ALGORITHM = settings.ALGORITHM;
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES;
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS;


class PasswordHasher:
    """비밀번호 해싱/검증 클래스"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        비밀번호를 bcrypt로 해싱합니다.
        
        Args:
            password: 평문 비밀번호
            
        Returns:
            str: 해싱된 비밀번호 (UTF-8 문자열)
        """
        # bcrypt로 해싱 (자동으로 salt 생성)
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        평문 비밀번호와 해시를 비교합니다.
        
        Args:
            plain_password: 평문 비밀번호
            hashed_password: 저장된 해시 비밀번호
            
        Returns:
            bool: 비밀번호 일치 여부
        """
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )


class JWTHandler:
    """JWT 토큰 생성/검증 클래스"""

    @staticmethod
    def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        JWT 액세스 토큰을 생성합니다.
        
        Args:
            data: 토큰에 포함할 데이터 (sub, role 등)
            expires_delta: 만료 시간 (기본값: 4시간)
            
        Returns:
            str: JWT 액세스 토큰
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "type": "access"  # 토큰 타입 명시
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        JWT 리프레시 토큰을 생성합니다.
        
        Args:
            data: 토큰에 포함할 데이터 (sub만 포함, 최소 정보)
            expires_delta: 만료 시간 (기본값: 3일)
            
        Returns:
            str: JWT 리프레시 토큰
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "type": "refresh"  # 토큰 타입 명시
        })
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
        """
        JWT 토큰을 검증하고 payload를 반환합니다.
        
        Args:
            token: JWT 토큰
            token_type: 토큰 타입 ("access" or "refresh")
            
        Returns:
            dict: 토큰 payload (검증 실패 시 None)
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # 토큰 타입 검증
            if payload.get("type") != token_type:
                return None
            
            return payload
        except InvalidTokenError:
            return None


# 싱글톤 인스턴스
password_hasher = PasswordHasher()
jwt_handler = JWTHandler()

