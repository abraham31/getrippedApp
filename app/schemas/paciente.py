from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import List, Dict, Optional

class PacienteCreate(BaseModel):
    nombre: str
    email: EmailStr
    sexo: str
    fecha_nacimiento: date
    peso: float = Field(..., gt=0)
    estatura: float = Field(..., gt=0)
    ciudad: Optional[str] = None
    telefono: Optional[str] = None
    actividad_laboral: Optional[str] = None
    actividad_fisica: Optional[str] = None
    horario_constancia: Optional[str] = None
    motivo_consulta: Optional[str] = None
    medicamentos: Optional[str] = None
    cirugias: Optional[str] = None
    alergias: Optional[str] = None
    antecedentes_heredofamiliares: Optional[str] = None
    consumo_sustancias: Optional[str] = None
    analisis_recientes: Optional[str] = None
    alimentos_preferencia: Optional[List[str]] = None
    alimentos_desagrado: Optional[List[Dict[str, int]]] = None  # [{"alimento": "X", "nivel": 5}]
    horarios_alimentacion: Optional[str] = None
    is_active: bool
    is_deleted: bool

class PacienteActivate(BaseModel):
    password: str = Field(..., min_length=6)

class PacienteUpdate(BaseModel):
    nombre: Optional[str] = None
    peso: Optional[float] = Field(None, gt=0)
    estatura: Optional[float] = Field(None, gt=0)
    objetivo: Optional[str] = None
    alergias: Optional[str] = None
    medicamentos: Optional[str] = None
    condiciones_medicas: Optional[str] = None
    actividad_fisica: Optional[str] = None
    preferencias_alimentarias: Optional[List[str]] = None
    observaciones: Optional[str] = None