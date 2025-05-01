from pydantic import BaseModel, Field


class VehicleSchema(BaseModel):
    brand: str = Field(..., max_length=50, min_length=1)
    model: str = Field(..., max_length=50, min_length=1)
    manufacture_year: int = Field(2000, ge=1970, le=3000)
    license_plate: str = Field(..., max_length=20, min_length=1)
    fuel_type: str = Field(..., max_length=20, min_length=1)


class VehicleCreateSchema(VehicleSchema):
    category_level_id: int


class VehicleUpdateSchema(VehicleCreateSchema):
    pass


class VehicleReadSchema(VehicleCreateSchema):
    id: int
