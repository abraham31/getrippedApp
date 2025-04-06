from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from typing import Literal

from app.schemas.consulta import ProgresoOut

class NotificacionResponse(BaseModel):
    id: str
    titulo: str
    mensaje: str
    fecha: datetime
    leido: bool
    progreso: Optional[ProgresoOut] = None
    tipo: Literal["progreso", "resumen_semana", "recordatorio", "otro"]

    class Config:
        from_attributes = True


