from pydantic import BaseModel, Field, HttpUrl, field_validator


class QRCodeGenerateRequest(BaseModel):
    """QR 코드 생성 요청"""
    url: str = Field(..., min_length=1, max_length=2000, description="QR 코드로 변환할 URL")
    size: int = Field(default=10, ge=1, le=50, description="QR 코드 크기 (1-50)")
    border: int = Field(default=2, ge=0, le=10, description="QR 코드 테두리 크기 (0-10)")

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """URL 검증"""
        if not v.strip():
            raise ValueError('URL은 비어있을 수 없습니다.')
        
        # http:// 또는 https://로 시작하지 않으면 자동 추가
        if not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        
        return v


class QRCodeBase64Response(BaseModel):
    """QR 코드 Base64 응답"""
    qrcode_base64: str = Field(..., description="Base64로 인코딩된 QR 코드 이미지")
    url: str = Field(..., description="QR 코드에 인코딩된 URL")
    size: int = Field(..., description="QR 코드 크기")
    format: str = Field(default="PNG", description="이미지 포맷")
