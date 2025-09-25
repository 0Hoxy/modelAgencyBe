import enum

# Enum 정의
class GenderEnum(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class CameraTestStatusEnum(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class VisaTypeEnum(enum.Enum):
    # 단기체류 (C)
    C_1 = "C-1"  # 외교
    C_2 = "C-2"  # 공무
    C_3 = "C-3"  # 관광통과
    C_4 = "C-4"  # 단기취업

    # 교수 (E)
    E_1 = "E-1"  # 교수
    E_2 = "E-2"  # 회화지도
    E_3 = "E-3"  # 연구
    E_4 = "E-4"  # 기술지도
    E_5 = "E-5"  # 전문직업
    E_6 = "E-6"  # 예술흥행
    E_7 = "E-7"  # 특정활동
    E_8 = "E-8"  # 연수취업
    E_9 = "E-9"  # 비전문취업
    E_10 = "E-10"  # 선원취업

    # 거주 (F)
    F_1 = "F-1"  # 방문동거
    F_2 = "F-2"  # 거주
    F_3 = "F-3"  # 동반
    F_4 = "F-4"  # 재외동포
    F_5 = "F-5"  # 영주
    F_6 = "F-6"  # 결혼이민

    # 기타 (H)
    H_1 = "H-1"  # 관광취업
    H_2 = "H-2"  # 방문취업

    # 기타활동 (D)
    D_1 = "D-1"  # 문화예술
    D_2 = "D-2"  # 유학
    D_3 = "D-3"  # 기술연수
    D_4 = "D-4"  # 일반연수
    D_5 = "D-5"  # 취재
    D_6 = "D-6"  # 종교
    D_7 = "D-7"  # 주재
    D_8 = "D-8"  # 기업투자
    D_9 = "D-9"  # 무역경영
    D_10 = "D-10"  # 구직

    # 외교 (A)
    A_1 = "A-1"  # 외교
    A_2 = "A-2"  # 공무
    A_3 = "A-3"  # 협정

    # 비자면제 (B)
    B_1 = "B-1"  # 사증면제
    B_2 = "B-2"  # 관광통과
