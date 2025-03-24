from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class ProgresoCreate(BaseModel):
    fecha: date
    peso: float = Field(..., gt=0)
    estatura: Optional[float] = Field(None, gt=0)
    circunferencia_cintura: Optional[float] = Field(None, gt=0)
    porcentaje_grasa_corporal: Optional[float] = Field(None, gt=0)
    observaciones: Optional[str] = None

class ProgresoResponse(BaseModel):
    id: str
    fecha: date
    peso: float
    estatura: Optional[float]
    circunferencia_cintura: Optional[float]
    porcentaje_grasa_corporal: Optional[float]
    observaciones: Optional[str]

    class Config:
        orm_mode = True