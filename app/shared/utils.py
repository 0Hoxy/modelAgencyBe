"""
공통 유틸리티 함수들
"""

import uuid
from datetime import datetime
from typing import Any, Dict

def generate_uuid() -> str:
    """UUID 생성"""
    return str(uuid.uuid4())

def format_datetime(dt: datetime) -> str:
    """날짜시간 포맷팅"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def create_response(data: Any, message: str = None, success: bool = True) -> Dict:
    """표준 응답 형식 생성"""
    return {
        "success": success,
        "data": data,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
