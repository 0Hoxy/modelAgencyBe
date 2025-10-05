import base64
from io import BytesIO
from typing import Tuple

import qrcode
from qrcode.image.pil import PilImage
from fastapi import HTTPException

from app.domain.qrcode.qrcode_schemas import QRCodeGenerateRequest, QRCodeBase64Response


class QRCodeService:
    """QR 코드 생성 서비스"""

    def generate_qrcode_image(
        self,
        request: QRCodeGenerateRequest
    ) -> Tuple[BytesIO, str]:
        """
        QR 코드 이미지 생성 (PNG)
        
        Args:
            request: QR 코드 생성 요청
            
        Returns:
            Tuple[BytesIO, str]: (이미지 바이트 스트림, URL)
            
        Raises:
            HTTPException: QR 코드 생성 실패
        """
        try:
            # QR 코드 생성기 설정
            qr = qrcode.QRCode(
                version=1,  # QR 코드 크기 (1-40, None이면 자동)
                error_correction=qrcode.constants.ERROR_CORRECT_H,  # 오류 수정 레벨 (최고)
                box_size=request.size,  # 각 박스의 픽셀 크기
                border=request.border,  # 테두리 크기
            )

            # 데이터 추가 및 생성
            qr.add_data(request.url)
            qr.make(fit=True)

            # PIL 이미지로 생성
            img = qr.make_image(fill_color="black", back_color="white")

            # BytesIO에 저장
            img_io = BytesIO()
            img.save(img_io, format='PNG')
            img_io.seek(0)

            return img_io, request.url

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"QR 코드 생성 중 오류가 발생했습니다: {str(e)}"
            )

    def generate_qrcode_base64(
        self,
        request: QRCodeGenerateRequest
    ) -> QRCodeBase64Response:
        """
        QR 코드를 Base64로 인코딩하여 반환
        
        Args:
            request: QR 코드 생성 요청
            
        Returns:
            QRCodeBase64Response: Base64 인코딩된 QR 코드
            
        Raises:
            HTTPException: QR 코드 생성 실패
        """
        try:
            # QR 코드 이미지 생성
            img_io, url = self.generate_qrcode_image(request)

            # Base64로 인코딩
            img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

            return QRCodeBase64Response(
                qrcode_base64=img_base64,
                url=url,
                size=request.size,
                format="PNG"
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"QR 코드 Base64 변환 중 오류가 발생했습니다: {str(e)}"
            )


qrcode_service = QRCodeService()
