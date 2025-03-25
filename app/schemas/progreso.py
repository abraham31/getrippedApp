from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class ProgresoCreate(BaseModel):
    fecha: date
    peso: float = Field(..., gt=0)
    masa_muscular: Optional[float] = Field(None, gt=0)
    masa_grasa: Optional[float] = Field(None, gt=0)
    porcentaje_grasa_corporal: Optional[float] = Field(None, gt=0)
    agua_corporal_total: Optional[float] = Field(None, gt=0)
    observaciones: Optional[str] = None


class ProgresoResponse(BaseModel):
    id: str
    fecha: date
    peso: float
    masa_muscular: Optional[float]
    masa_grasa: Optional[float]
    porcentaje_grasa_corporal: Optional[float]
    agua_corporal_total: Optional[float]
    observaciones: Optional[str]

    class Config:
        from_attributes = True