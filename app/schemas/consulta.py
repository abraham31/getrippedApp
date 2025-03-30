from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class ProgresoInput(BaseModel):
    peso: float = Field(..., gt=0)
    masa_muscular: Optional[float] = Field(None, gt=0)
    masa_grasa: Optional[float] = Field(None, gt=0)
    porcentaje_grasa_corporal: Optional[float] = Field(None, gt=0)
    agua_corporal_total: Optional[float] = Field(None, gt=0)

class ConsultaCreate(BaseModel):
    fecha: Optional[date] = None
    tipo: str = Field(..., description="primera o seguimiento")
    progreso: ProgresoInput
    observaciones: Optional[str] = None

class ProgresoOut(BaseModel):
    peso: float
    masa_muscular: Optional[float]
    masa_grasa: Optional[float]
    porcentaje_grasa_corporal: Optional[float]
    agua_corporal_total: Optional[float]

class ConsultaOut(BaseModel):
    fecha: date
    tipo: str
    progreso: ProgresoOut
    observaciones: Optional[str]
