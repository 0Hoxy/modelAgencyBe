아아= Field(..., description="카메라테스트 상태")
    visited_at: datetime | None = Field(default=None, description="방문일시")

# --- Read 스키마 (변경 없음) ---
class ReadBase(BaseModel, OrmConfigMixin):
    id: uuid.UUID

class ReadDomesticModel(CreateDomesticModel, ReadBase):
    pass

class ReadOverseaModel(CreateOverseaModel, ReadBase):
    pass

class CreateModelResponse(BaseModel, OrmConfigMixin):
    name: str
    message: str = "님의 접수가 완료되었습니다."