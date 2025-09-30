from typing import Literal, Annotated, Any
from phonenumbers import is_valid_number, parse, NumberParseException, PhoneNumberFormat, format_number
from phonenumbers.phonenumber import PhoneNumber
from pydantic import BeforeValidator, PlainSerializer, WithJsonSchema

# Literal 타입을 사용하여 허용되는 포맷을 명시
PhoneFormat = Literal["E164", "INTERNATIONAL", "NATIONAL"]


def validate_phone(v: str | PhoneNumber) -> PhoneNumber:
    """
    전화번호를 검증하고 PhoneNumber 객체로 변환합니다.

    Args:
        v: 전화번호 문자열 또는 PhoneNumber 객체
           - E.164 형식 권장: +821012345678
           - 한국 번호는 숫자만: 01012345678

    Returns:
        PhoneNumber: 검증된 PhoneNumber 객체

    Raises:
        ValueError: 유효하지 않은 전화번호일 경우
    """
    # v가 PhoneNumber 객체 타입인가?
    if isinstance(v, PhoneNumber):
        # PhoneNumber 객체라면 전화번가 실제로 할당/사용이 가능한 전화번호인 검증한다.
        if not is_valid_number(v):
            #유효하지 않다면 ValueError 발생
            raise ValueError('유효하지 않은 전화번호 객체입니다.')
        # 유효하다면 반환
        return v

    # v가 str이 아니거나 비어있는가?
    if not isinstance(v, str) or not v:
        # 비어있다면 ValueError 발생
        raise ValueError('전화번호는 비어있지 않은 문자열이어야 합니다.')

    # E.164 형식 시도 (+로 시작)
    if v.startswith('+'):
        try:
            #phonenumbers.parse 함수 호출, E.164형식이므로 지역코드가 필요하지 않음
            phone = parse(v, None) # phone이 PhoneNumber 객체가 되어 country_code(+82)와 national_number(1012341234)로 분해되어 저장된다.
            #PhoneNumber 객체를 유효한 번호인지 실질적 검증
            if is_valid_number(phone):
                #옳다면 PhoneNumber 객체를 반환
                return phone
        #파싱함수 실패 시 예외 발생(형식이 너무 이상하거나, 전화번호가 아닌 문자열)
        except NumberParseException as e:
            raise ValueError(f'유효하지 않은 국제 전화번호 형식입니다: {e}')
        #파싱은 성공했으나 is_valid_number가 실패한 경우
        raise ValueError('유효하지 않은 국제 전화번호입니다.')

    # 숫자만 있는지 확인
    if not v.isdigit():
        raise ValueError('전화번호는 숫자만 입력하거나 +로 시작하는 국제 형식이어야 합니다.')

    # 한국 번호로 시도
    try:
        #한국번호로 파싱
        phone = parse(v, "KR")
        #유효한 번호일 경우 PhoneNumber 객체 반환
        if is_valid_number(phone):
            return phone
    # 파싱함수 실패 시 예외 발생(지역정보는 있으므로 형식이 너무 이상하거나, 전화번호가 아닌 문자열)
    except NumberParseException:
        pass  # 예외가 발생해도 최종 에러로 넘어감

    #한국 번호로 파싱 성공했지만 is_valid_number()가 False, 한국 번호로 파싱 자체가 실패 (너무 짧거나 이상한 형식)
    raise ValueError(
        '유효하지 않은 전화번호 형식입니다. '
        'E.164 형식(예: +821012345678) 또는 한국 번호(예: 01012345678)로 입력해주세요.'
    )


def validate_phone_optional(v: str | PhoneNumber | None) -> PhoneNumber | None:
    """
    선택적 전화번호 검증 (None 또는 빈 문자열을 None으로 처리)

    Args:
        v: 전화번호 문자열, PhoneNumber 객체, None 또는 빈 문자열

    Returns:
        PhoneNumber | None: 검증된 PhoneNumber 객체 또는 None

    Note:
        빈 문자열('')은 None으로 처리됩니다.
    """
    if v is None or (isinstance(v, str) and not v):
        return None
    return validate_phone(v)


def serialize_phone(phone: PhoneNumber, format_: PhoneFormat = "NATIONAL") -> str:
    """
    PhoneNumber 객체를 지정된 형식의 문자열로 직렬화합니다.

    Args:
        phone: PhoneNumber 객체
        format_: 출력 형식
            - "E164": +821012345678
            - "INTERNATIONAL": +82 10-1234-5678
            - "NATIONAL": 010-1234-5678 (기본값)

    Returns:
        str: 포맷된 전화번호 문자열
    """
    format_map = {
        "E164": PhoneNumberFormat.E164,
        "INTERNATIONAL": PhoneNumberFormat.INTERNATIONAL,
        "NATIONAL": PhoneNumberFormat.NATIONAL,
    }
    phone_format = format_map[format_]  # Literal 타입이므로 항상 존재
    return format_number(phone, phone_format)


def serialize_phone_optional(
    phone: PhoneNumber | None,
    format_: PhoneFormat = "NATIONAL"
) -> str | None:
    """
    선택적 PhoneNumber 객체를 문자열로 직렬화합니다. (None 허용)

    Args:
        phone: PhoneNumber 객체 또는 None
        format_: 출력 형식 (기본값: "NATIONAL")

    Returns:
        str | None: 포맷된 전화번호 문자열 또는 None
    """
    if phone is None:
        return None
    # 올바른 직렬화 함수를 호출하도록 수정
    return serialize_phone(phone, format_)


# Pydantic Annotated 타입 정의
# 이 타입들을 사용하면 Pydantic이 PhoneNumber를 이해할 수 있습니다.
# 베이스 타입은 Any를 사용하여 Pydantic이 직접 PhoneNumber를 처리하지 않도록 합니다.

ValidatedPhoneNumber = Annotated[
    Any,  # PhoneNumber 타입이 실제 런타임 타입이지만, Pydantic에게는 Any로 알림
    BeforeValidator(validate_phone),  # 입력값을 PhoneNumber로 변환
    PlainSerializer(lambda p: serialize_phone(p, "E164")),  # JSON 직렬화 시 E164 형식 사용
    WithJsonSchema({"type": "string", "example": "+821012345678"}),  # OpenAPI 문서용 스키마
]

ValidatedPhoneNumberOptional = Annotated[
    Any,  # PhoneNumber | None 타입이 실제 런타임 타입이지만, Pydantic에게는 Any로 알림
    BeforeValidator(validate_phone_optional),  # 입력값을 PhoneNumber | None으로 변환
    PlainSerializer(lambda p: serialize_phone_optional(p, "E164") if p else None),  # JSON 직렬화
    WithJsonSchema({"type": "string", "example": "+821012345678", "nullable": True}),  # OpenAPI 문서용 스키마
]