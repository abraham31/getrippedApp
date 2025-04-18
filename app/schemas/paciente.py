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
    horario_constante: Optional[str] = None  # antes "horario_constancia"
    motivo_consulta: Optional[str] = None
    medicamentos: Optional[str] = None
    cirugias: Optional[str] = None
    alergias: Optional[str] = None
    antecedentes_heredofamiliares: Optional[str] = None
    consumo_sustancias: Optional[str] = None
    analisis_recientes: Optional[str] = None
    alimentos_preferidos: Optional[List[str]] = None  # antes "alimentos_preferencia"
    alimentos_desagrado: Optional[List[Dict[str, int]]] = None  # [{"alimento": "X", "nivel": 5}]
    horarios_alimentacion: Optional[str] = None

class PacienteStatusUpdate(BaseModel):
    is_active: bool

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

class PacienteOut(BaseModel):
    id: str
    nombre: str
    email: EmailStr
    is_active: bool
    sexo: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    peso: Optional[float] = None
    estatura: Optional[float] = None


class ComidaCumplida(BaseModel):
    nombre: str  # Ej: "desayuno", "colación 1"
    cumplido: bool

class CumplimientoDia(BaseModel):
    dia: str  # Ej: "Lunes", "Martes"
    comidas: List[ComidaCumplida]

class CumplimientoSemana(BaseModel):
    semana: int  # Ej: 1, 2, 3 según el número de la semana del plan
    cumplimiento: List[CumplimientoDia]

class ComidaCumplidaInput(BaseModel):
    nombre: str  # Ej: "desayuno", "colación 1"
    cumplido: bool

class CumplimientoDiaInput(BaseModel):
    dia: str  # Ej: "Lunes"
    comidas: List[ComidaCumplidaInput]

class SeleccionIngrediente(BaseModel):
    dia: str
    comida: str
    ingrediente: str
    seleccionado: dict  # Debe incluir al menos nombre y cantidad

class SeleccionesPaciente(BaseModel):
    selecciones: List[SeleccionIngrediente]