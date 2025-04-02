from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class ProgresoInput(BaseModel):
    peso: float = Field(..., gt=0, description="Peso actual del paciente en kg")
    masa_muscular: Optional[float] = Field(None, gt=0, description="Masa muscular actual en kg")
    masa_grasa: Optional[float] = Field(None, gt=0, description="Masa grasa actual en kg")
    porcentaje_grasa_corporal: Optional[float] = Field(None, gt=0, description="Porcentaje de grasa corporal actual")
    agua_corporal_total: Optional[float] = Field(None, gt=0, description="Cantidad de agua corporal total actual en litros o porcentaje")

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
    id: str = Field(..., alias="_id")
    fecha: date
    tipo: str
    progreso: ProgresoOut
    observaciones: Optional[str] = None

    class Config:
        populate_by_name = True
