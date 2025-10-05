from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.domain.qrcode.qrcode_service import qrcode_service
from app.domain.qrcode.qrcode_schemas import (
    QRCodeGenerateRequest,
    QRCodeBase64Response,
)

app = APIRouter(
    prefix="/qrcode",
    tags=["qrcode"],
    responses={404: {"description": "Not found"}},
)


@app.post("/generate", response_class=StreamingResponse)
async def generate_qrcode_image(request: QRCodeGenerateRequest):
    """
    QR 코드 이미지 생성 (PNG)
    
    URL을 QR 코드 이미지로 변환하여 PNG 파일로 반환합니다.
    
    - **url**: QR 코드로 변환할 URL (http:// 또는 https:// 생략 가능)
    - **size**: QR 코드 크기 (1-50, 기본값: 10)
    - **border**: 테두리 크기 (0-10, 기본값: 2)
    
    **Returns**: PNG 이미지 파일
    
    **사용 예시**:
    ```bash
    curl -X POST "http://localhost:8000/qrcode/generate" \\
      -H "Content-Type: application/json" \\
      -d '{"url": "https://example.com"}' \\
      --output qrcode.png
    ```
    """
    img_io, url = qrcode_service.generate_qrcode_image(request)
    
    return StreamingResponse(
        img_io,
        media_type="image/png",
        headers={
            "Content-Disposition": f'attachment; filename="qrcode_{url[:30]}.png"'
        }
    )


@app.post("/generate/base64", response_model=QRCodeBase64Response)
async def generate_qrcode_base64(request: QRCodeGenerateRequest):
    """
    QR 코드 Base64 생성
    
    URL을 QR 코드로 변환하여 Base64 인코딩된 문자열로 반환합니다.
    웹/모바일 앱에서 즉시 이미지로 표시할 수 있습니다.
    
    - **url**: QR 코드로 변환할 URL (http:// 또는 https:// 생략 가능)
    - **size**: QR 코드 크기 (1-50, 기본값: 10)
    - **border**: 테두리 크기 (0-10, 기본값: 2)
    
    **Returns**: Base64로 인코딩된 QR 코드 이미지
    
    **사용 예시**:
    ```bash
    curl -X POST "http://localhost:8000/qrcode/generate/base64" \\
      -H "Content-Type: application/json" \\
      -d '{"url": "https://example.com"}'
    ```
    
    **HTML에서 사용**:
    ```html
    <img src="data:image/png;base64,{qrcode_base64}" alt="QR Code">
    ```
    """
    return qrcode_service.generate_qrcode_base64(request)


@app.get("/test")
async def test_qrcode():
    """
    QR 코드 테스트 엔드포인트
    
    기본 설정으로 Google 홈페이지 QR 코드를 PNG로 반환합니다.
    """
    request = QRCodeGenerateRequest(
        url="https://www.google.com",
        size=10,
        border=2
    )
    
    img_io, url = qrcode_service.generate_qrcode_image(request)
    
    return StreamingResponse(
        img_io,
        media_type="image/png",
        headers={
            "Content-Disposition": 'attachment; filename="test_qrcode.png"'
        }
    )