from pydantic import BaseModel, Field


class CabinetSchema(BaseModel):
    name: str = Field(..., max_length=16, min_length=1)


class CabinetCreateSchema(CabinetSchema):
    pass


class CabinetUpdateSchema(CabinetSchema):
    pass


class CabinetReadSchema(CabinetSchema):
    id: int
