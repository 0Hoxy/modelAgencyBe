from datetime import datetime

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.domain.excel.excel_service import excel_service

app = APIRouter(
    prefix="/excel",
    tags=["excel"],
    responses={404: {"description": "Not found"}},
)


@app.get("/domestic")
async def get_domestic_models_excel():
    """
    국내 모델 리스트 엑셀 다운로드
    
    국내 모델의 모든 정보를 엑셀 파일(.xlsx)로 다운로드합니다.
    
    **포함 정보**:
    - 기본 정보: ID, 이름, 예명, 생년월일, 성별, 전화번호, 국적
    - 소속사 정보: 소속사명, 담당자, 전화번호
    - SNS: 인스타그램, 틱톡, 유튜브
    - 주소: 도시, 구/군, 상세주소
    - 기타: 특기, 언어, 타투 정보
    - 신체: 키, 몸무게, 의류 사이즈
    
    **파일명**: `국내모델목록_YYYYMMDD_HHMMSS.xlsx`
    
    **사용 예시**:
    ```bash
    curl -X GET "http://localhost:8000/excel/domestic" --output domestic_models.xlsx
    ```
    
    또는 브라우저에서:
    ```
    http://localhost:8000/excel/domestic
    ```
    """
    excel_io = await excel_service.generate_domestic_excel()
    
    # 현재 시간으로 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"국내모델목록_{timestamp}.xlsx"
    
    return StreamingResponse(
        excel_io,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


@app.get("/global")
async def get_global_models_excel():
    """
    해외 모델 리스트 엑셀 다운로드
    
    해외 모델의 모든 정보를 엑셀 파일(.xlsx)로 다운로드합니다.
    
    **포함 정보**:
    - 기본 정보: ID, 이름, 예명, 생년월일, 성별, 전화번호, 국적
    - SNS: 인스타그램, 유튜브, 카카오톡
    - 주소: 도시, 구/군, 상세주소
    - 언어: 모국어, 기타 언어, 한국어 수준
    - 기타: 특기, 타투 정보, 비자 타입
    - 신체: 키, 몸무게, 의류 사이즈
    
    **파일명**: `해외모델목록_YYYYMMDD_HHMMSS.xlsx`
    
    **사용 예시**:
    ```bash
    curl -X GET "http://localhost:8000/excel/global" --output global_models.xlsx
    ```
    
    또는 브라우저에서:
    ```
    http://localhost:8000/excel/global
    ```
    """
    excel_io = await excel_service.generate_global_excel()
    
    # 현재 시간으로 파일명 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"해외모델목록_{timestamp}.xlsx"
    
    return StreamingResponse(
        excel_io,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )