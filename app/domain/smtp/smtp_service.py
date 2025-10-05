"""
SMTP 서비스
- 임시 비밀번호 생성 및 발송
"""
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException

from app.core.db import db
from app.core.config import settings
from app.shared import password_hasher
from app.domain.accounts.account_repository import AccountRepository
from app.domain.smtp.smtp_schemas import TempPasswordRequest, TempPasswordResponse


class SMTPService:
    def __init__(self):
        self.account_repository = AccountRepository()

    def _generate_temp_password(self) -> str:
        """
        임시 비밀번호 생성
        - 12자리
        - 영어 대문자, 소문자, 숫자, 특수문자 각 최소 1개 포함
        """
        # 각 카테고리에서 최소 1개씩 선택
        password_chars = [
            random.choice(string.ascii_uppercase),  # 대문자 1개
            random.choice(string.ascii_lowercase),  # 소문자 1개
            random.choice(string.digits),  # 숫자 1개
            random.choice("!@#$%^&*()"),  # 특수문자 1개
        ]
        
        # 나머지 8자리는 모든 문자에서 랜덤 선택
        all_chars = string.ascii_uppercase + string.ascii_lowercase + string.digits + "!@#$%^&*()"
        password_chars.extend(random.choices(all_chars, k=8))
        
        # 섞기
        random.shuffle(password_chars)
        
        return ''.join(password_chars)

    async def _send_email(self, to_email: str, temp_password: str) -> None:
        """
        SMTP를 통해 임시 비밀번호 이메일 발송
        """
        try:
            # 이메일 내용 작성
            message = MIMEMultipart("alternative")
            message["Subject"] = f"[{settings.APP_NAME}] 임시 비밀번호 발급"
            message["From"] = settings.SMTP_FROM_EMAIL
            message["To"] = to_email

            # HTML 이메일 본문
            html_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                        <h2 style="color: #4CAF50; text-align: center;">임시 비밀번호 발급</h2>
                        <p>안녕하세요,</p>
                        <p>요청하신 임시 비밀번호가 발급되었습니다.</p>
                        <div style="background-color: #f4f4f4; padding: 15px; border-radius: 5px; margin: 20px 0;">
                            <p style="margin: 0;"><strong>임시 비밀번호:</strong></p>
                            <p style="font-size: 20px; color: #4CAF50; font-weight: bold; margin: 10px 0; letter-spacing: 2px;">
                                {temp_password}
                            </p>
                        </div>
                        <p style="color: #d32f2f;">⚠️ 보안을 위해 로그인 후 반드시 비밀번호를 변경해주세요.</p>
                        <p style="color: #999; font-size: 12px; margin-top: 30px;">
                            본 메일은 발신 전용입니다. 문의사항이 있으시면 고객센터로 연락해주세요.
                        </p>
                    </div>
                </body>
            </html>
            """

            # Plain text 버전 (HTML 지원 안 되는 클라이언트용)
            text_content = f"""
            [{settings.APP_NAME}] 임시 비밀번호 발급

            안녕하세요,
            요청하신 임시 비밀번호가 발급되었습니다.

            임시 비밀번호: {temp_password}

            ⚠️ 보안을 위해 로그인 후 반드시 비밀번호를 변경해주세요.

            본 메일은 발신 전용입니다.
            """

            # 텍스트와 HTML 파트 추가
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            message.attach(part1)
            message.attach(part2)

            # SMTP 서버 연결 및 전송
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()  # TLS 암호화
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(message)

        except smtplib.SMTPException as e:
            raise HTTPException(
                status_code=500,
                detail=f"이메일 발송 중 오류가 발생했습니다: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"이메일 발송 중 예기치 않은 오류가 발생했습니다: {str(e)}"
            )

    async def send_temp_password(self, request: TempPasswordRequest) -> TempPasswordResponse:
        """
        임시 비밀번호 생성 및 발송
        1. 계정 존재 확인
        2. 임시 비밀번호 생성
        3. DB에 해시화하여 저장
        4. 이메일 발송
        """
        try:
            # 1. 계정 존재 확인
            user = await self.account_repository.get_by_pid(request.pid)
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="해당 이메일로 등록된 계정을 찾을 수 없습니다."
                )

            # 2. 임시 비밀번호 생성
            temp_password = self._generate_temp_password()

            # 3. 비밀번호 해시화 및 DB 저장
            hashed_password = password_hasher.hash_password(temp_password)
            async with db.transaction() as conn:
                await self.account_repository.update_password_transaction(
                    conn=conn,
                    pid=request.pid,
                    new_password=hashed_password
                )

            # 4. 이메일 발송
            await self._send_email(request.pid, temp_password)

            return TempPasswordResponse(
                message="임시 비밀번호가 이메일로 발송되었습니다. 로그인 후 비밀번호를 변경해주세요.",
                email=request.pid
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"임시 비밀번호 발급 중 오류가 발생했습니다: {str(e)}"
            )


# Singleton 인스턴스
smtp_service = SMTPService()
