from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal, Optional

class CitaCreate(BaseModel):
    fecha: datetime
    motivo: str = Field(..., max_length=255)

class CitaUpdate(BaseModel):
    fecha: Optional[datetime] = None
    estado: Optional[Literal["activa", "cancelada", "finalizada"]] = None
    motivo: Optional[str] = None

class CitaOut(BaseModel):
    id: str = Field(..., alias="_id")
    paciente_id: str
    fecha: datetime
    motivo: str
    estado: Literal["activa", "cancelada", "finalizada"]

class Config:
    populate_by_name = True
